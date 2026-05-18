"""
Friend-finding feature — full implementation.

Features:
- Anketa wizard (name -> age -> looking_for -> gender -> city -> interests -> bio -> photo)
- AI bio writer (auto-generates polished bio)
- Match preferences (target gender, age range, same-city only)
- Browse with Like/Pass + Block/Report
- Match flow with AI-generated icebreakers
- "Who liked you" view (premium sees names, free sees count)
- Daily like quota (free: 5, premium: unlimited)
- Photo verification (gpt-4o vision)
"""
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    get_friend_profile,
    upsert_friend_profile,
    update_friend_photos,
    deactivate_friend_profile,
    reactivate_friend_profile,
    delete_friend_profile,
    get_next_browse_profile,
    record_friend_reaction,
    get_friend_matches,
    count_friend_likes_received,
    get_users_who_liked_me,
    get_friend_preferences,
    upsert_friend_preferences,
    block_user,
    is_blocked,
    get_friend_daily_usage,
    increment_friend_likes,
    get_photo_verification,
    upsert_photo_verification,
    is_premium_active,
)
from mindmate.ai.engines.friend_finder_engine import write_bio, generate_icebreakers
from mindmate.ai.photo_verification import verify_photos
from mindmate.ai.moderation import moderate_image
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import (
    FRIEND_LOOKING_OPTIONS,
    FRIEND_GENDER_OPTIONS,
    FRIEND_INTERESTS,
    FRIEND_MIN_AGE,
    FRIEND_MAX_AGE,
    FRIEND_MIN_INTERESTS,
    FRIEND_MAX_INTERESTS,
    FRIEND_BIO_MAX_LENGTH,
    FRIEND_MAX_PHOTOS,
    FRIEND_PHOTO_MIN_FILE_SIZE,
    FRIEND_PHOTO_MAX_FILE_SIZE,
    FRIEND_PHOTO_MIN_DIMENSION,
    FREE_DAILY_LIKES,
)


def _get_first_photo(profile: dict) -> Optional[str]:
    """Get the first photo file_id from a profile (handles old single + new array)."""
    photos = profile.get("photo_file_ids") or []
    if photos:
        return photos[0]
    return profile.get("photo_file_id")


def _get_all_photos(profile: dict) -> list:
    """Get all photo file_ids."""
    photos = profile.get("photo_file_ids") or []
    if photos:
        return list(photos)
    legacy = profile.get("photo_file_id")
    return [legacy] if legacy else []

logger = logging.getLogger(__name__)


# ──────────────────────── Keyboards ────────────────────────

def kb_friends_main(profile: dict, is_verified: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    """Main friends menu when profile exists."""
    is_active = profile.get("is_active", True)
    visibility_btn = (
        InlineKeyboardButton(t("friends.btn_hide", lang), callback_data="friends_hide")
        if is_active else
        InlineKeyboardButton(t("friends.btn_show", lang), callback_data="friends_show")
    )
    verify_btn = (
        InlineKeyboardButton(t("friends.btn_verified", lang), callback_data="friends_verified_info")
        if is_verified else
        InlineKeyboardButton(t("friends.btn_verify_start", lang), callback_data="friends_verify_start")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_browse", lang), callback_data="friends_browse")],
        [
            InlineKeyboardButton(t("friends.btn_myprofile", lang), callback_data="friends_myprofile"),
            InlineKeyboardButton(t("friends.btn_matches", lang), callback_data="friends_matches"),
        ],
        [
            InlineKeyboardButton(t("friends.btn_likes", lang), callback_data="friends_likes"),
            verify_btn,
        ],
        [
            InlineKeyboardButton(t("friends.btn_filters", lang), callback_data="friends_prefs"),
            InlineKeyboardButton(t("friends.btn_edit", lang), callback_data="friends_edit"),
        ],
        [
            visibility_btn,
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ])


def kb_browse_actions(candidate_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Like/Pass + Block buttons during browsing."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("friends.btn_pass", lang), callback_data="friends_pass"),
            InlineKeyboardButton(t("friends.btn_like", lang), callback_data="friends_like"),
        ],
        [
            InlineKeyboardButton(t("friends.btn_block", lang), callback_data=f"friends_block_{candidate_id}"),
            InlineKeyboardButton(t("friends.btn_stop_browse", lang), callback_data="friends_back"),
        ],
    ])


def kb_match_actions(match_user_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """When a match is created, offer to open chat or get icebreakers."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            t("friends.btn_write", lang),
            url=f"tg://user?id={match_user_id}",
        )],
        [InlineKeyboardButton(
            t("friends.btn_icebreakers", lang),
            callback_data=f"friends_icebreakers_{match_user_id}",
        )],
        [InlineKeyboardButton(t("friends.btn_continue_browse", lang), callback_data="friends_browse")],
    ])


def kb_looking_for(lang: str = "uz") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(f"friends.looking_for.{lf}", lang), callback_data=f"friends_lf_{lf}")]
        for lf in FRIEND_LOOKING_OPTIONS
    ]
    rows.append([InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")])
    return InlineKeyboardMarkup(rows)


def kb_gender(lang: str = "uz") -> InlineKeyboardMarkup:
    """Gender is required so users can be matched correctly — no skip option."""
    rows = [
        [InlineKeyboardButton(t(f"friends.gender.{g}", lang), callback_data=f"friends_g_{g}")]
        for g in FRIEND_GENDER_OPTIONS
    ]
    rows.append([InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")])
    return InlineKeyboardMarkup(rows)


def kb_interests(selected: list, lang: str = "uz") -> InlineKeyboardMarkup:
    """Multi-select interests (with checkmarks for selected ones)."""
    rows = []
    row = []
    for interest in FRIEND_INTERESTS:
        mark = "✅ " if interest in selected else ""
        label = t(f"friends.interests.{interest}", lang)
        row.append(InlineKeyboardButton(
            f"{mark}{label}",
            callback_data=f"friends_i_{interest}",
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        t("friends.btn_confirm_interests", lang).format(count=len(selected), max=FRIEND_MAX_INTERESTS),
        callback_data="friends_i_done",
    )])
    rows.append([InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")])
    return InlineKeyboardMarkup(rows)


def kb_bio_step(lang: str = "uz") -> InlineKeyboardMarkup:
    """Bio step: type your own OR let AI write."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_ai_bio", lang), callback_data="friends_bio_ai")],
        [InlineKeyboardButton(t("friends.btn_skip_bio", lang), callback_data="friends_bio_skip")],
    ])


def kb_photo_step(count: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Photo step keyboard — adapts to how many photos the user has uploaded."""
    rows = []
    if count > 0:
        rows.append([InlineKeyboardButton(
            t("friends.btn_confirm_photos", lang).format(count=count, max=FRIEND_MAX_PHOTOS),
            callback_data="friends_photos_done",
        )])
        rows.append([InlineKeyboardButton(
            t("friends.btn_clear_photos", lang),
            callback_data="friends_photos_clear",
        )])
    if count == 0:
        rows.append([InlineKeyboardButton(
            t("friends.btn_skip_photos", lang),
            callback_data="friends_photos_skip",
        )])
    rows.append([InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")])
    return InlineKeyboardMarkup(rows)


def kb_edit_choices(lang: str = "uz") -> InlineKeyboardMarkup:
    """Sub-menu when the user wants to edit something."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_edit_photos", lang), callback_data="friends_edit_photos")],
        [InlineKeyboardButton(t("friends.btn_edit_full", lang), callback_data="friends_edit_full")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
    ])


def kb_preferences(prefs: dict, lang: str = "uz") -> InlineKeyboardMarkup:
    """Filters keyboard."""
    target = prefs.get("target_gender")
    target_label = t(f"friends.gender.{target}", lang) if target in FRIEND_GENDER_OPTIONS else t("friends.pref_any", lang)
    same_city = prefs.get("same_city_only", True)
    same_city_label = t("friends.pref_yes", lang) if same_city else t("friends.pref_no", lang)
    age_label = f"{prefs.get('min_age', 18)}-{prefs.get('max_age', 100)}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.pref_gender_btn", lang).format(label=target_label), callback_data="friends_pref_gender")],
        [InlineKeyboardButton(t("friends.pref_age_btn", lang).format(label=age_label), callback_data="friends_pref_age")],
        [InlineKeyboardButton(
            t("friends.pref_city_btn", lang).format(label=same_city_label),
            callback_data="friends_pref_city",
        )],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
    ])


def kb_pref_gender_select(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_gender_male", lang), callback_data="friends_setg_male")],
        [InlineKeyboardButton(t("friends.btn_gender_female", lang), callback_data="friends_setg_female")],
        [InlineKeyboardButton(t("friends.btn_gender_any", lang), callback_data="friends_setg_any")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_prefs")],
    ])


# ──────────────────────── Handlers ────────────────────────

async def friends_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point — /friends or menu button."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        profile = await get_friend_profile(user.id)

        if not profile:
            await chat.send_message(
                t("friends.teaser", lang),
                reply_markup=kb_teaser(lang),
                parse_mode="Markdown",
            )
        else:
            await _show_friends_main(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in friends_handler: {e}")
        await chat.send_message(t("errors.generic", "en"))


def kb_teaser(lang: str = "uz") -> InlineKeyboardMarkup:
    """Initial teaser keyboard — opt-in to wizard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_create", lang), callback_data="friends_start_setup")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ])


def kb_wizard_cancel(lang: str = "uz") -> InlineKeyboardMarkup:
    """Cancel-only keyboard for wizard text-input steps."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")],
    ])


def kb_wizard_back_cancel(back_callback: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Back-to-previous-step + cancel for wizard text steps."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("buttons.back", lang), callback_data=back_callback)],
        [InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_wizard_cancel")],
    ])


async def _show_friends_main(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: dict,
    lang: str,
    chat=None,
    edit_query=None,
) -> None:
    """Render the friends-feature dashboard."""
    name = profile.get("display_name", "—")
    age = profile.get("age", "—")
    lf_key = profile.get("looking_for", "")
    looking = t(f"friends.looking_for.{lf_key}", lang) if lf_key in FRIEND_LOOKING_OPTIONS else "—"
    visibility = t("friends.visibility_active", lang) if profile.get("is_active") else t("friends.visibility_hidden", lang)

    likes_received = await count_friend_likes_received(profile["user_id"])
    is_pro = await is_premium_active(profile["user_id"])
    likes_text = t("friends.likes_text", lang).format(count=likes_received)
    if not is_pro and likes_received > 0:
        likes_text += t("friends.likes_premium_hint", lang)

    verification = await get_photo_verification(profile["user_id"])
    is_verified = bool(verification and verification.get("is_verified"))
    verified_badge = t("friends.verified_badge", lang) if is_verified else t("friends.not_verified_badge", lang)

    text = (
        f"{t('friends.dashboard_title', lang)}\n\n"
        f"👤 {name}, {age}\n"
        f"🎯 {looking}\n"
        f"{visibility} · {verified_badge}\n\n"
        f"{likes_text}\n\n"
        f"{t('friends.dashboard_prompt', lang)}"
    )

    kb = kb_friends_main(profile, is_verified, lang)
    if edit_query:
        try:
            await edit_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
            return
        except Exception:
            pass
    if chat:
        await chat.send_message(text, reply_markup=kb, parse_mode="Markdown")


async def friends_show_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the friends edit choices menu (called from profile hub)."""
    query = update.callback_query
    user = query.from_user
    try:
        try:
            await query.answer()
        except Exception:
            pass
        lang = await user_service.get_user_language(user.id)
        await query.edit_message_text(
            t("friends.edit_title", lang),
            reply_markup=kb_edit_choices(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"friends_show_edit_menu error: {e}")


async def friends_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle friends_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        # ── Start wizard (opt-in from teaser) ─────────────────────
        if data == "friends_start_setup":
            context.user_data["friends_setup"] = {"step": "name", "data": {}}
            await query.edit_message_text(
                t("friends.wizard_name", lang),
                reply_markup=kb_wizard_cancel(lang),
                parse_mode="Markdown",
            )
            return

        # ── Cancel wizard ─────────────────────────────────────────
        if data == "friends_wizard_cancel":
            context.user_data.pop("friends_setup", None)
            context.user_data.pop("friends_edit_photos_state", None)
            existing = await get_friend_profile(user.id)
            if existing:
                await _show_friends_main(update, context, existing, lang, edit_query=query)
            else:
                await query.edit_message_text(
                    t("friends.teaser", lang),
                    reply_markup=kb_teaser(lang),
                    parse_mode="Markdown",
                )
            return

        # ── Setup wizard: looking_for ─────────────────────────────
        if data.startswith("friends_lf_"):
            looking = data.replace("friends_lf_", "")
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["looking_for"] = looking
            setup["step"] = "gender"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                t("friends.wizard_gender", lang),
                reply_markup=kb_gender(lang),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard: gender ──────────────────────────────────
        if data.startswith("friends_g_"):
            tag = data.replace("friends_g_", "")
            if tag not in FRIEND_GENDER_OPTIONS:
                await query.answer(t("friends.validation_gender", lang), show_alert=True)
                return
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["gender"] = tag
            setup["step"] = "city"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                t("friends.wizard_city", lang),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard: interests ───────────────────────────────
        if data.startswith("friends_i_"):
            tag = data.replace("friends_i_", "")
            setup = context.user_data.get("friends_setup", {})
            interests = setup.setdefault("data", {}).setdefault("interests", [])

            if tag == "done":
                if len(interests) < FRIEND_MIN_INTERESTS:
                    await query.answer(
                        t("friends.validation_interests_min", lang).format(min=FRIEND_MIN_INTERESTS),
                        show_alert=True,
                    )
                    return
                setup["step"] = "bio"
                context.user_data["friends_setup"] = setup
                await query.edit_message_text(
                    t("friends.wizard_bio", lang).format(max_len=FRIEND_BIO_MAX_LENGTH),
                    reply_markup=kb_bio_step(lang),
                    parse_mode="Markdown",
                )
                return

            if tag in interests:
                interests.remove(tag)
            else:
                if len(interests) >= FRIEND_MAX_INTERESTS:
                    await query.answer(
                        t("friends.validation_interests_max", lang).format(max=FRIEND_MAX_INTERESTS),
                        show_alert=True,
                    )
                    return
                interests.append(tag)
            setup["data"]["interests"] = interests
            context.user_data["friends_setup"] = setup
            await query.edit_message_reply_markup(reply_markup=kb_interests(interests, lang))
            return

        # ── Setup wizard: bio choice ──────────────────────────────
        if data == "friends_bio_skip":
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["bio"] = ""
            setup["step"] = "photos"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                t("friends.wizard_photos", lang).format(max=FRIEND_MAX_PHOTOS),
                reply_markup=kb_photo_step(0, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_bio_ai":
            setup = context.user_data.get("friends_setup", {})
            data_dict = setup.get("data", {})
            await query.edit_message_text(t("friends.wizard_ai_bio_loading", lang), parse_mode="Markdown")
            try:
                bio = await write_bio(data_dict, lang)
            except Exception as e:
                logger.error(f"AI bio failed: {e}")
                bio = ""
            data_dict["bio"] = bio[:FRIEND_BIO_MAX_LENGTH]
            setup["data"] = data_dict
            setup["step"] = "photos"
            context.user_data["friends_setup"] = setup
            preview = bio if bio else t("friends.wizard_ai_bio_error", lang)
            await query.edit_message_text(
                t("friends.wizard_ai_bio_done", lang).format(bio=preview, max=FRIEND_MAX_PHOTOS),
                reply_markup=kb_photo_step(0, lang),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard / edit photos: done / skip / clear ──────
        if data == "friends_photos_skip":
            if context.user_data.get("friends_edit_photos_state"):
                await _finalize_photos_edit(update, context)
            else:
                await _finalize_friend_setup(update, context, photo_file_ids=[])
            return

        if data == "friends_photos_done":
            if context.user_data.get("friends_edit_photos_state"):
                await _finalize_photos_edit(update, context)
            else:
                setup = context.user_data.get("friends_setup", {})
                photos = setup.get("data", {}).get("photo_file_ids", [])
                await _finalize_friend_setup(update, context, photo_file_ids=photos)
            return

        if data == "friends_photos_clear":
            if context.user_data.get("friends_edit_photos_state"):
                context.user_data["friends_edit_photos_state"] = {"photos": []}
            else:
                setup = context.user_data.get("friends_setup", {})
                data_dict = setup.setdefault("data", {})
                data_dict["photo_file_ids"] = []
                setup["data"] = data_dict
                context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                t("friends.photo_cleared", lang).format(max=FRIEND_MAX_PHOTOS),
                reply_markup=kb_photo_step(0, lang),
                parse_mode="Markdown",
            )
            return

        # ── Main menu actions ─────────────────────────────────────
        profile = await get_friend_profile(user.id)
        if not profile:
            await friends_handler(update, context)
            return

        if data == "menu_friends" or data == "friends_back":
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_myprofile":
            await _show_my_profile(query, profile, user.id, lang)
            return

        if data == "friends_matches":
            await _show_matches(query, user.id, lang)
            return

        if data == "friends_likes":
            await _show_likes_received(query, user.id, lang)
            return

        if data == "friends_prefs":
            prefs = await get_friend_preferences(user.id) or {}
            await query.edit_message_text(
                t("friends.pref_title", lang),
                reply_markup=kb_preferences(prefs, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_pref_gender":
            await query.edit_message_text(
                t("friends.pref_gender_title", lang),
                reply_markup=kb_pref_gender_select(lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("friends_setg_"):
            choice = data.replace("friends_setg_", "")
            target = None if choice == "any" else choice
            prefs = await get_friend_preferences(user.id) or {}
            await upsert_friend_preferences(
                user_id=user.id,
                target_gender=target,
                min_age=prefs.get("min_age", 18),
                max_age=prefs.get("max_age", 100),
                same_city_only=prefs.get("same_city_only", True),
            )
            prefs = await get_friend_preferences(user.id)
            await query.edit_message_text(
                t("friends.pref_title", lang),
                reply_markup=kb_preferences(prefs, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_pref_age":
            context.user_data["friends_pref_age"] = True
            await query.edit_message_text(
                t("friends.pref_age_title", lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_pref_city":
            prefs = await get_friend_preferences(user.id) or {}
            new_value = not prefs.get("same_city_only", True)
            await upsert_friend_preferences(
                user_id=user.id,
                target_gender=prefs.get("target_gender"),
                min_age=prefs.get("min_age", 18),
                max_age=prefs.get("max_age", 100),
                same_city_only=new_value,
            )
            prefs = await get_friend_preferences(user.id)
            await query.edit_message_text(
                t("friends.pref_title", lang),
                reply_markup=kb_preferences(prefs, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit":
            await query.edit_message_text(
                t("friends.edit_title", lang),
                reply_markup=kb_edit_choices(lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit_photos":
            context.user_data["friends_edit_photos_state"] = {"photos": []}
            context.user_data.pop("friends_setup", None)
            await query.edit_message_text(
                t("friends.wizard_photos", lang).format(max=FRIEND_MAX_PHOTOS),
                reply_markup=kb_photo_step(0, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit_full":
            await delete_friend_profile(user.id)
            context.user_data.pop("friends_setup", None)
            context.user_data.pop("friends_edit_photos_state", None)
            try:
                await query.delete_message()
            except Exception:
                pass
            await friends_handler(update, context)
            return

        if data == "friends_hide":
            await deactivate_friend_profile(user.id)
            await query.answer(t("friends.hide_answer", lang), show_alert=False)
            profile = await get_friend_profile(user.id)
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_show":
            await reactivate_friend_profile(user.id)
            await query.answer(t("friends.show_answer", lang), show_alert=False)
            profile = await get_friend_profile(user.id)
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_browse":
            if not await is_premium_active(user.id):
                usage = await get_friend_daily_usage(user.id)
                if usage["likes_given"] >= FREE_DAILY_LIKES:
                    await query.edit_message_text(
                        t("friends.browse_like_quota", lang).format(limit=FREE_DAILY_LIKES),
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(t("menu.premium", lang), callback_data="menu_premium")],
                            [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
                        ]),
                        parse_mode="Markdown",
                    )
                    return
            await _show_next_profile(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_like":
            await _react(update, context, is_like=True)
            return

        if data == "friends_pass":
            await _react(update, context, is_like=False)
            return

        if data.startswith("friends_block_"):
            try:
                blocked_id = int(data.replace("friends_block_", ""))
            except ValueError:
                return
            await block_user(user.id, blocked_id, reason="block")
            await query.answer(t("friends.browse_blocked_answer", lang), show_alert=False)
            context.user_data.pop("browsing_candidate_id", None)
            my_profile = await get_friend_profile(user.id)
            await _show_next_profile(update, context, my_profile, lang, edit_query=query)
            return

        if data.startswith("friends_icebreakers_"):
            try:
                other_id = int(data.replace("friends_icebreakers_", ""))
            except ValueError:
                return
            await query.answer(t("friends.icebreakers_loading", lang), show_alert=False)
            other = await get_friend_profile(other_id)
            if not other:
                return
            try:
                qs = await generate_icebreakers(profile, other, lang)
            except Exception as e:
                logger.error(f"Icebreakers gen failed: {e}")
                qs = []
            text = t("friends.icebreakers_title", lang)
            text += "\n\n".join(f"• _{q}_" for q in qs) if qs else t("friends.icebreakers_error", lang)
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        t("friends.btn_write", lang),
                        url=f"tg://user?id={other_id}",
                    )],
                    [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
                ]),
                parse_mode="Markdown",
            )
            return

        # ── Photo verification ─────────────────────────────────────
        if data == "friends_verify_start":
            if not profile.get("photo_file_id") and not _get_first_photo(profile):
                await query.edit_message_text(
                    t("friends.verify_no_photo", lang),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back"),
                    ]]),
                )
                return
            context.user_data["friends_verify"] = True
            await query.edit_message_text(
                t("friends.verify_intro", lang),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t("buttons.cancel", lang), callback_data="friends_back"),
                ]]),
                parse_mode="Markdown",
            )
            return

        if data == "friends_verified_info":
            await query.answer(t("friends.verified_info", lang), show_alert=True)
            return

        # legacy
        if data == "friends_waitlist":
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

    except Exception as e:
        logger.error(f"Error in friends_callback: {e}")
        try:
            await query.edit_message_text(t("errors.generic", "en"))
        except Exception:
            pass


async def friends_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text inputs during the friend setup wizard or preferences edit."""
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    lang = await user_service.get_user_language(user.id)

    # ── Age range edit ────────────────────────────────────────────
    if context.user_data.get("friends_pref_age"):
        try:
            parts = text.replace("–", "-").split("-")
            if len(parts) != 2:
                raise ValueError
            min_age = int(parts[0].strip())
            max_age = int(parts[1].strip())
            if min_age < 18 or max_age > 100 or min_age >= max_age:
                raise ValueError
        except ValueError:
            await message.reply_text(
                t("friends.pref_age_error", lang),
                parse_mode="Markdown",
            )
            return
        prefs = await get_friend_preferences(user.id) or {}
        await upsert_friend_preferences(
            user_id=user.id,
            target_gender=prefs.get("target_gender"),
            min_age=min_age,
            max_age=max_age,
            same_city_only=prefs.get("same_city_only", True),
        )
        context.user_data.pop("friends_pref_age", None)
        prefs = await get_friend_preferences(user.id)
        await message.reply_text(
            t("friends.pref_age_updated", lang),
            reply_markup=kb_preferences(prefs, lang),
        )
        return

    setup = context.user_data.get("friends_setup")
    if not setup:
        return

    step = setup.get("step")
    data = setup.setdefault("data", {})

    if step == "name":
        if len(text) < 2 or len(text) > 50:
            await message.reply_text(
                t("friends.validation_name", lang),
                reply_markup=kb_wizard_cancel(lang),
            )
            return
        data["display_name"] = text
        setup["step"] = "age"
        await message.reply_text(
            t("friends.wizard_age", lang).format(min_age=FRIEND_MIN_AGE),
            reply_markup=kb_wizard_cancel(lang),
            parse_mode="Markdown",
        )
        return

    if step == "age":
        try:
            age = int(text)
            if age < FRIEND_MIN_AGE or age > FRIEND_MAX_AGE:
                raise ValueError
        except ValueError:
            await message.reply_text(
                t("friends.validation_age", lang).format(min=FRIEND_MIN_AGE, max=FRIEND_MAX_AGE),
                reply_markup=kb_wizard_cancel(lang),
            )
            return
        data["age"] = age
        setup["step"] = "looking_for"
        await message.reply_text(
            t("friends.wizard_looking", lang),
            reply_markup=kb_looking_for(lang),
            parse_mode="Markdown",
        )
        return

    if step == "city":
        if len(text) < 2 or len(text) > 100:
            await message.reply_text(
                t("friends.validation_city", lang),
                reply_markup=kb_wizard_cancel(lang),
            )
            return
        data["city"] = text
        setup["step"] = "interests"
        data.setdefault("interests", [])
        await message.reply_text(
            t("friends.wizard_interests", lang).format(min=FRIEND_MIN_INTERESTS, max=FRIEND_MAX_INTERESTS),
            reply_markup=kb_interests([], lang),
            parse_mode="Markdown",
        )
        return

    if step == "bio":
        bio = "" if text in ("-", "—", "skip") else text
        if len(bio) > FRIEND_BIO_MAX_LENGTH:
            await message.reply_text(
                t("friends.validation_bio", lang).format(length=len(bio), max=FRIEND_BIO_MAX_LENGTH),
                reply_markup=kb_wizard_cancel(lang),
            )
            return
        data["bio"] = bio
        setup["step"] = "photos"
        data.setdefault("photo_file_ids", [])
        await message.reply_text(
            t("friends.wizard_photos", lang).format(max=FRIEND_MAX_PHOTOS),
            reply_markup=kb_photo_step(0, lang),
            parse_mode="Markdown",
        )
        return


async def _resolve_to_photo_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message,
) -> Optional[str]:
    """Resolve any image submission to a Telegram photo file_id."""
    if message.photo:
        return message.photo[-1].file_id

    if message.document:
        mime = message.document.mime_type or ""
        if not mime.startswith("image/"):
            return None
        try:
            doc_file = await message.document.get_file()
            doc_bytes = await doc_file.download_as_bytearray()
            sent = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=bytes(doc_bytes),
            )
            return sent.photo[-1].file_id
        except Exception as e:
            logger.error(f"Failed to convert document image to photo: {e}")
            lang = context.user_data.get("_cached_lang", "en")
            await message.reply_text(
                t("friends.error_doc_convert", lang),
                parse_mode="Markdown",
            )
            return None

    return None


def _check_photo_quality(message, lang: str = "en") -> Optional[str]:
    """Run cheap pre-checks (size, dimensions). Returns error string or None."""
    file_size = None
    width = None
    height = None

    if message.photo:
        largest = message.photo[-1]
        file_size = largest.file_size
        width = largest.width
        height = largest.height
    elif message.document:
        file_size = message.document.file_size
        if message.document.thumbnail:
            width = message.document.thumbnail.width
            height = message.document.thumbnail.height

    if file_size is not None:
        if file_size < FRIEND_PHOTO_MIN_FILE_SIZE:
            return t("friends.photo_quality_small", lang)
        if file_size > FRIEND_PHOTO_MAX_FILE_SIZE:
            return t("friends.photo_quality_large", lang)

    if width and height:
        if min(width, height) < FRIEND_PHOTO_MIN_DIMENSION:
            return t("friends.photo_quality_dim", lang, w=width, h=height, min_dim=FRIEND_PHOTO_MIN_DIMENSION)

    return None


async def _moderate_photo_bytes(file_id: str, context) -> tuple:
    """Download a photo by file_id and moderate it. Returns (approved, reason)."""
    try:
        f = await context.bot.get_file(file_id)
        photo_bytes = await f.download_as_bytearray()
        result = await moderate_image(bytes(photo_bytes))
        return result.approved, result.reason
    except Exception as e:
        logger.error(f"Moderation download failed: {e}")
        return True, ""


async def friends_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive a photo: either anketa photo OR verification selfie OR edit-photo flow."""
    setup = context.user_data.get("friends_setup")
    is_verifying = context.user_data.get("friends_verify")
    is_editing_photos = context.user_data.get("friends_edit_photos_state")

    message = update.message
    if not message:
        return

    in_photo_step = bool(setup and setup.get("step") == "photos")
    if not (is_verifying or in_photo_step or is_editing_photos):
        return

    lang = context.user_data.get("_cached_lang", "en")

    quality_error = _check_photo_quality(message, lang)
    if quality_error:
        await message.reply_text(quality_error)
        return

    photo_file_id = await _resolve_to_photo_id(update, context, message)
    if not photo_file_id:
        return

    # ── Verification selfie ──────────────────────────────────────
    if is_verifying:
        await _handle_verification_photo(update, context, photo_file_id)
        return

    # AI content moderation
    await message.chat.send_action("typing")
    approved, reason = await _moderate_photo_bytes(photo_file_id, context)
    if not approved:
        text = t("friends.error_moderation", lang)
        if reason:
            text += f"\n\n_{reason}_"
        text += t("friends.error_moderation_suffix", lang)
        await message.reply_text(text, parse_mode="Markdown")
        return

    # ── Editing photos only (post-anketa) ────────────────────────
    if is_editing_photos:
        photos = is_editing_photos.get("photos", [])
        if len(photos) >= FRIEND_MAX_PHOTOS:
            await message.reply_text(t("friends.photo_max_error", lang).format(max=FRIEND_MAX_PHOTOS))
            return
        photos.append(photo_file_id)
        is_editing_photos["photos"] = photos
        context.user_data["friends_edit_photos_state"] = is_editing_photos
        await message.reply_text(
            t("friends.photo_accepted", lang).format(count=len(photos), max=FRIEND_MAX_PHOTOS),
            reply_markup=kb_photo_step(len(photos), lang),
        )
        return

    # ── Anketa photo accumulator (multi-photo) ───────────────────
    if in_photo_step:
        data = setup.setdefault("data", {})
        photos = data.setdefault("photo_file_ids", [])
        if len(photos) >= FRIEND_MAX_PHOTOS:
            await message.reply_text(t("friends.photo_max_error", lang).format(max=FRIEND_MAX_PHOTOS))
            return
        photos.append(photo_file_id)
        data["photo_file_ids"] = photos
        setup["data"] = data
        context.user_data["friends_setup"] = setup
        await message.reply_text(
            t("friends.photo_accepted", lang).format(count=len(photos), max=FRIEND_MAX_PHOTOS),
            reply_markup=kb_photo_step(len(photos), lang),
        )
        return


async def _handle_verification_photo(
    update: Update, context: ContextTypes.DEFAULT_TYPE, photo_file_id: str,
) -> None:
    """Run the photo verification flow on a freshly-uploaded selfie."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        await chat.send_action("typing")
        lang = await user_service.get_user_language(user.id)
        profile = await get_friend_profile(user.id)
        first_photo = _get_first_photo(profile) if profile else None
        if not first_photo:
            await chat.send_message(t("friends.verify_no_saved", lang))
            context.user_data.pop("friends_verify", None)
            return

        saved_file = await context.bot.get_file(first_photo)
        saved_bytes = await saved_file.download_as_bytearray()

        selfie_file = await context.bot.get_file(photo_file_id)
        selfie_bytes = await selfie_file.download_as_bytearray()

        await chat.send_message(t("friends.verify_loading", lang))
        verified, note = await verify_photos(bytes(saved_bytes), bytes(selfie_bytes))
        await upsert_photo_verification(user.id, verified, note)

        context.user_data.pop("friends_verify", None)

        if verified:
            await chat.send_message(
                t("friends.verify_success", lang).format(note=note),
                parse_mode="Markdown",
            )
        else:
            await chat.send_message(
                t("friends.verify_fail", lang).format(note=note),
                parse_mode="Markdown",
            )

        profile = await get_friend_profile(user.id)
        await _show_friends_main(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Verification flow error: {e}")
        _err_lang = context.user_data.get("_cached_lang", "en")
        await chat.send_message(t("friends.verify_error", _err_lang))


async def _finalize_friend_setup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_file_ids: Optional[list] = None,
) -> None:
    """Save the assembled profile and show the dashboard."""
    user = update.effective_user
    setup = context.user_data.get("friends_setup", {})
    data = setup.get("data", {})
    lang = await user_service.get_user_language(user.id)

    try:
        await upsert_friend_profile(
            user_id=user.id,
            display_name=data.get("display_name", "—"),
            age=data.get("age", FRIEND_MIN_AGE),
            looking_for=data.get("looking_for", "friendship"),
            gender=data.get("gender"),
            city=data.get("city"),
            interests=data.get("interests", []),
            bio=data.get("bio"),
            photo_file_ids=photo_file_ids or [],
            is_active=True,
        )
    except Exception as e:
        logger.error(f"Error saving friend profile: {e}")
        await update.effective_chat.send_message(t("friends.error_save", lang))
        return

    context.user_data.pop("friends_setup", None)
    profile = await get_friend_profile(user.id)

    await update.effective_chat.send_message(
        t("friends.wizard_done", lang),
        parse_mode="Markdown",
    )
    await _show_friends_main(update, context, profile, lang, chat=update.effective_chat)


async def _finalize_photos_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Save photos-only edit and show the dashboard."""
    user = update.effective_user
    lang = await user_service.get_user_language(user.id)
    state = context.user_data.get("friends_edit_photos_state", {})
    photos = state.get("photos", [])

    try:
        await update_friend_photos(user.id, photos)
    except Exception as e:
        logger.error(f"Error updating photos: {e}")
        await update.effective_chat.send_message(t("friends.error_photos_save", lang))
        return

    context.user_data.pop("friends_edit_photos_state", None)
    profile = await get_friend_profile(user.id)
    await update.effective_chat.send_message(
        t("friends.photos_saved", lang).format(count=len(photos)),
        parse_mode="Markdown",
    )
    await _show_friends_main(update, context, profile, lang, chat=update.effective_chat)


# ──────────────────────── Browsing ────────────────────────

async def _show_next_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    my_profile: dict,
    lang: str,
    edit_query=None,
) -> None:
    """Show the next candidate profile to the user."""
    user_id = my_profile["user_id"]
    looking = my_profile.get("looking_for")
    city = my_profile.get("city")

    prefs = await get_friend_preferences(user_id) or {}
    target_gender = prefs.get("target_gender")
    min_age = prefs.get("min_age", 18)
    max_age = prefs.get("max_age", 100)
    same_city_only = prefs.get("same_city_only", True)

    candidate = await get_next_browse_profile(
        viewer_id=user_id,
        looking_for=looking,
        same_city=city if same_city_only else None,
        target_gender=target_gender,
        min_age=min_age,
        max_age=max_age,
    )

    if not candidate and same_city_only:
        candidate = await get_next_browse_profile(
            viewer_id=user_id,
            looking_for=looking,
            target_gender=target_gender,
            min_age=min_age,
            max_age=max_age,
        )

    if not candidate:
        text = t("friends.browse_no_profiles", lang)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("friends.btn_filters", lang), callback_data="friends_prefs")],
            [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
        ])
        if edit_query:
            try:
                await edit_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
                return
            except Exception:
                pass
        await update.effective_chat.send_message(text, reply_markup=kb, parse_mode="Markdown")
        return

    context.user_data["browsing_candidate_id"] = candidate["user_id"]

    cand_verification = await get_photo_verification(candidate["user_id"])
    is_verified = bool(cand_verification and cand_verification.get("is_verified"))

    photos = _get_all_photos(candidate)
    photo_count = len(photos)

    card_text = _format_profile_card(candidate, verified=is_verified, photo_count=photo_count, lang=lang)
    kb = kb_browse_actions(candidate["user_id"], lang)

    if photos:
        if edit_query:
            try:
                await edit_query.delete_message()
            except Exception:
                pass
        await update.effective_chat.send_photo(
            photo=photos[0],
            caption=card_text,
            reply_markup=kb,
            parse_mode="Markdown",
        )
    else:
        if edit_query:
            try:
                await edit_query.edit_message_text(card_text, reply_markup=kb, parse_mode="Markdown")
                return
            except Exception:
                pass
        await update.effective_chat.send_message(card_text, reply_markup=kb, parse_mode="Markdown")


def _format_profile_card(profile: dict, verified: bool = False, photo_count: int = 0, lang: str = "uz") -> str:
    """Render a profile card."""
    name = profile.get("display_name", "—")
    age = profile.get("age", "")
    city = profile.get("city", "")
    lf_key = profile.get("looking_for", "")
    looking = t(f"friends.looking_for.{lf_key}", lang) if lf_key in FRIEND_LOOKING_OPTIONS else "—"
    interests = profile.get("interests") or []
    interests_str = " · ".join(
        t(f"friends.interests.{i}", lang) for i in interests[:6]
    )
    bio = profile.get("bio") or ""

    badge = " ✅" if verified else ""
    parts = [f"✨ *{name}, {age}*{badge}"]
    if city:
        parts.append(f"📍 {city}")
    parts.append(f"🎯 {looking}")
    if photo_count > 1:
        parts.append(t("friends.photo_count", lang).format(count=photo_count))
    if interests_str:
        parts.append(f"\n{interests_str}")
    if bio:
        parts.append(f"\n_{bio}_")

    return "\n".join(parts)


async def _react(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    is_like: bool,
) -> None:
    """Record a like/pass and show match dialog or continue."""
    query = update.callback_query
    user = query.from_user
    lang = await user_service.get_user_language(user.id)
    candidate_id = context.user_data.get("browsing_candidate_id")
    if not candidate_id:
        my_profile = await get_friend_profile(user.id)
        await _show_next_profile(update, context, my_profile, lang, edit_query=query)
        return

    if is_like and not await is_premium_active(user.id):
        usage = await get_friend_daily_usage(user.id)
        if usage["likes_given"] >= FREE_DAILY_LIKES:
            await query.answer(
                t("friends.browse_like_limit_answer", lang).format(limit=FREE_DAILY_LIKES),
                show_alert=True,
            )
            return

    if await is_blocked(user.id, candidate_id):
        context.user_data.pop("browsing_candidate_id", None)
        my_profile = await get_friend_profile(user.id)
        await _show_next_profile(update, context, my_profile, lang, edit_query=query)
        return

    is_match = await record_friend_reaction(user.id, candidate_id, is_like)
    context.user_data.pop("browsing_candidate_id", None)
    if is_like:
        await increment_friend_likes(user.id)

    if is_match and is_like:
        candidate = await get_friend_profile(candidate_id)
        text = t("friends.match_text", lang).format(name=candidate.get("display_name", "—"))
        try:
            await query.delete_message()
        except Exception:
            pass
        await update.effective_chat.send_message(
            text,
            reply_markup=kb_match_actions(candidate_id, lang),
            parse_mode="Markdown",
        )
        return

    my_profile = await get_friend_profile(user.id)
    await _show_next_profile(update, context, my_profile, lang, edit_query=query)


# ──────────────────────── My profile / Matches / Likes views ────────────────────────

async def _show_my_profile(query, profile: dict, user_id: int, lang: str) -> None:
    """Show the user their own profile."""
    from telegram import InputMediaPhoto

    verification = await get_photo_verification(user_id)
    is_verified = bool(verification and verification.get("is_verified"))
    photos = _get_all_photos(profile)
    text = t("friends.myprofile_title", lang) + _format_profile_card(
        profile, verified=is_verified, photo_count=len(photos), lang=lang,
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("friends.btn_change_photos", lang), callback_data="friends_edit_photos")],
        [InlineKeyboardButton(t("friends.btn_full_edit", lang), callback_data="friends_edit_full")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
    ])

    if not photos:
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
        return

    try:
        await query.delete_message()
    except Exception:
        pass

    chat = query.message.chat

    if len(photos) > 1:
        media = [InputMediaPhoto(media=p) for p in photos[:10]]
        try:
            await chat.send_media_group(media=media)
        except Exception as e:
            logger.error(f"send_media_group failed: {e}")
        await chat.send_message(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await chat.send_photo(
            photo=photos[0],
            caption=text,
            reply_markup=kb,
            parse_mode="Markdown",
        )


async def _show_matches(query, user_id: int, lang: str) -> None:
    matches = await get_friend_matches(user_id)
    if not matches:
        await query.edit_message_text(
            t("friends.matches_empty", lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("friends.btn_browse", lang), callback_data="friends_browse")],
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    lines = [t("friends.matches_title", lang)]
    rows = []
    for m in matches[:10]:
        lines.append(f"• *{m['display_name']}*, {m['age']} — _{m.get('city', '—')}_")
        rows.append([InlineKeyboardButton(
            f"💬 {m['display_name']}",
            url=f"tg://user?id={m['user_id']}",
        )])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")])
    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )


async def _show_likes_received(query, user_id: int, lang: str) -> None:
    """Show users who liked me (premium: full profiles, free: count only)."""
    is_pro = await is_premium_active(user_id)
    count = await count_friend_likes_received(user_id)

    if count == 0:
        await query.edit_message_text(
            t("friends.likes_none", lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    if not is_pro:
        await query.edit_message_text(
            t("friends.likes_count_free", lang).format(count=count),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("friends.btn_get_premium", lang), callback_data="menu_premium")],
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    profiles = await get_users_who_liked_me(user_id)
    lines = [t("friends.likes_count_premium", lang).format(count=count)]
    for p in profiles[:10]:
        lines.append(f"• *{p['display_name']}*, {p['age']} — _{p.get('city', '—')}_")
    if not profiles:
        lines.append(t("friends.likes_later", lang))
    rows = [[InlineKeyboardButton(t("friends.btn_start_browsing", lang), callback_data="friends_browse")]]
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")])
    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )
