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
    FRIEND_LOOKING_LABELS_UZ,
    FRIEND_GENDER_OPTIONS,
    FRIEND_GENDER_LABELS_UZ,
    FRIEND_INTERESTS,
    FRIEND_INTERESTS_LABELS_UZ,
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
        InlineKeyboardButton("🙈 Anketani yashirish", callback_data="friends_hide")
        if is_active else
        InlineKeyboardButton("👁 Anketani ko'rsat", callback_data="friends_show")
    )
    verify_btn = (
        InlineKeyboardButton("✅ Tasdiqlangan", callback_data="friends_verified_info")
        if is_verified else
        InlineKeyboardButton("🛡 Anketani tasdiqlash", callback_data="friends_verify_start")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💝 Tanishuv boshlash", callback_data="friends_browse")],
        [
            InlineKeyboardButton("✨ Mening anketam", callback_data="friends_myprofile"),
            InlineKeyboardButton("💌 Match'lar", callback_data="friends_matches"),
        ],
        [
            InlineKeyboardButton("💖 Sizni yoqtirganlar", callback_data="friends_likes"),
            verify_btn,
        ],
        [
            InlineKeyboardButton("🎯 Filtrlar", callback_data="friends_prefs"),
            InlineKeyboardButton("⚙️ Tahrirlash", callback_data="friends_edit"),
        ],
        [
            visibility_btn,
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ])


def kb_browse_actions(candidate_id: int) -> InlineKeyboardMarkup:
    """Like/Pass + Block buttons during browsing."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ O'tib ketish", callback_data="friends_pass"),
            InlineKeyboardButton("❤️ Yoqdi", callback_data="friends_like"),
        ],
        [
            InlineKeyboardButton("🚫 Bloklash", callback_data=f"friends_block_{candidate_id}"),
            InlineKeyboardButton("⏸ Tanishuvni to'xtatish", callback_data="friends_back"),
        ],
    ])


def kb_match_actions(match_user_id: int) -> InlineKeyboardMarkup:
    """When a match is created, offer to open chat or get icebreakers."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💬 Telegram'da yozish",
            url=f"tg://user?id={match_user_id}",
        )],
        [InlineKeyboardButton(
            "💡 Suhbat boshlovchi savollar",
            callback_data=f"friends_icebreakers_{match_user_id}",
        )],
        [InlineKeyboardButton("➡️ Tanishuvni davom ettirish", callback_data="friends_browse")],
    ])


def kb_looking_for() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(FRIEND_LOOKING_LABELS_UZ[lf], callback_data=f"friends_lf_{lf}")]
        for lf in FRIEND_LOOKING_OPTIONS
    ])


def kb_gender() -> InlineKeyboardMarkup:
    """Gender is required so users can be matched correctly — no skip option."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(FRIEND_GENDER_LABELS_UZ[g], callback_data=f"friends_g_{g}")]
        for g in FRIEND_GENDER_OPTIONS
    ])


def kb_interests(selected: list[str]) -> InlineKeyboardMarkup:
    """Multi-select interests (with checkmarks for selected ones)."""
    rows = []
    row = []
    for interest in FRIEND_INTERESTS:
        mark = "✅ " if interest in selected else ""
        label = FRIEND_INTERESTS_LABELS_UZ.get(interest, interest)
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
        f"✅ Tasdiqlash ({len(selected)} tanlandi)",
        callback_data="friends_i_done",
    )])
    return InlineKeyboardMarkup(rows)


def kb_bio_step() -> InlineKeyboardMarkup:
    """Bio step: type your own OR let AI write."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ AI bio yozib bersin", callback_data="friends_bio_ai")],
        [InlineKeyboardButton("⏭ Bio'siz davom etish", callback_data="friends_bio_skip")],
    ])


def kb_photo_step(count: int) -> InlineKeyboardMarkup:
    """Photo step keyboard — adapts to how many photos the user has uploaded."""
    rows = []
    if count > 0:
        rows.append([InlineKeyboardButton(
            f"✅ Tasdiqlash ({count}/{FRIEND_MAX_PHOTOS} rasm)",
            callback_data="friends_photos_done",
        )])
        rows.append([InlineKeyboardButton(
            "🗑 Boshqatdan boshlash",
            callback_data="friends_photos_clear",
        )])
    if count == 0:
        rows.append([InlineKeyboardButton(
            "⏭ Rasmsiz davom etish",
            callback_data="friends_photos_skip",
        )])
    return InlineKeyboardMarkup(rows)


def kb_edit_choices(lang: str = "uz") -> InlineKeyboardMarkup:
    """Sub-menu when the user wants to edit something."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Faqat rasmlarni o'zgartirish", callback_data="friends_edit_photos")],
        [InlineKeyboardButton("📝 Anketani to'liq qayta yozish", callback_data="friends_edit_full")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="friends_back")],
    ])


def kb_preferences(prefs: dict) -> InlineKeyboardMarkup:
    """Filters keyboard."""
    target = prefs.get("target_gender")
    target_label = FRIEND_GENDER_LABELS_UZ.get(target, "Hammasi") if target else "Hammasi"
    same_city = prefs.get("same_city_only", True)
    same_city_label = "Ha" if same_city else "Yo'q"
    age_label = f"{prefs.get('min_age', 18)}-{prefs.get('max_age', 100)}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👤 Jins: {target_label}", callback_data="friends_pref_gender")],
        [InlineKeyboardButton(f"🎂 Yosh oraligi: {age_label}", callback_data="friends_pref_age")],
        [InlineKeyboardButton(
            f"📍 Faqat shahrim: {same_city_label}",
            callback_data="friends_pref_city",
        )],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
    ])


def kb_pref_gender_select() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👨 Erkak", callback_data="friends_setg_male")],
        [InlineKeyboardButton("👩 Ayol", callback_data="friends_setg_female")],
        [InlineKeyboardButton("🌈 Hammasi", callback_data="friends_setg_any")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_prefs")],
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
            await chat.send_message(t("friends.teaser", lang), parse_mode="Markdown")
            await chat.send_message(
                "✨ *Anketa yaratish*\n\n"
                "Avval ismingizni kiriting (Telegram'dagi ismingiz yoki taxallus):",
                parse_mode="Markdown",
            )
            context.user_data["friends_setup"] = {
                "step": "name",
                "data": {},
            }
        else:
            await _show_friends_main(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in friends_handler: {e}")
        await chat.send_message("Do'st topish")


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
    looking = FRIEND_LOOKING_LABELS_UZ.get(profile.get("looking_for", ""), "—")
    visibility = "👁 Ko'rinmoqda" if profile.get("is_active") else "🙈 Yashirin"

    likes_received = await count_friend_likes_received(profile["user_id"])
    is_pro = await is_premium_active(profile["user_id"])
    likes_text = (
        f"💖 Sizni yoqtirganlar: *{likes_received}*"
    )
    if not is_pro and likes_received > 0:
        likes_text += " _(Premium'da kim ekanligi)_"

    verification = await get_photo_verification(profile["user_id"])
    is_verified = bool(verification and verification.get("is_verified"))
    verified_badge = "✅ Tasdiqlangan" if is_verified else "🔓 Tasdiqlanmagan"

    text = (
        f"💝 *Do'st topish*\n\n"
        f"👤 {name}, {age}\n"
        f"🎯 {looking}\n"
        f"{visibility} · {verified_badge}\n\n"
        f"{likes_text}\n\n"
        f"_Bugun yangi tanishuv?_"
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


async def friends_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle friends_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        # ── Setup wizard: looking_for ─────────────────────────────
        if data.startswith("friends_lf_"):
            looking = data.replace("friends_lf_", "")
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["looking_for"] = looking
            setup["step"] = "gender"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                "👤 *Jinsingizni tanlang*\n\n"
                "_(Boshqa foydalanuvchilar sizni shunga qarab topishadi)_",
                reply_markup=kb_gender(),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard: gender ──────────────────────────────────
        if data.startswith("friends_g_"):
            tag = data.replace("friends_g_", "")
            if tag not in FRIEND_GENDER_OPTIONS:
                await query.answer("Iltimos, jinsingizni tanlang", show_alert=True)
                return
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["gender"] = tag
            setup["step"] = "city"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                "🌆 *Shahringiz qaysi?*\n\n"
                "Iltimos, shahar nomini yozing.\n"
                "_Misol: Toshkent, Samarqand, Buxoro_",
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
                        f"Kamida {FRIEND_MIN_INTERESTS} ta qiziqish tanlang!",
                        show_alert=True,
                    )
                    return
                setup["step"] = "bio"
                context.user_data["friends_setup"] = setup
                await query.edit_message_text(
                    "✨ *O'zingiz haqingizda qisqa yozing*\n\n"
                    "1-3 jumla — kim ekanligingiz va qanday odamni qidirayapsiz.\n\n"
                    f"_Maksimum {FRIEND_BIO_MAX_LENGTH} ta belgi._\n\n"
                    "Yoki AI'dan yordam oling — anketa ma'lumotlaringiz asosida "
                    "siz uchun bio yozadi:",
                    reply_markup=kb_bio_step(),
                    parse_mode="Markdown",
                )
                return

            if tag in interests:
                interests.remove(tag)
            else:
                if len(interests) >= FRIEND_MAX_INTERESTS:
                    await query.answer(
                        f"Maksimum {FRIEND_MAX_INTERESTS} ta tanlay olasiz",
                        show_alert=True,
                    )
                    return
                interests.append(tag)
            setup["data"]["interests"] = interests
            context.user_data["friends_setup"] = setup
            await query.edit_message_reply_markup(reply_markup=kb_interests(interests))
            return

        # ── Setup wizard: bio choice ──────────────────────────────
        if data == "friends_bio_skip":
            setup = context.user_data.get("friends_setup", {})
            setup.setdefault("data", {})["bio"] = ""
            setup["step"] = "photos"
            context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                f"📸 *Profilingizga rasm qo'shing*\n\n"
                f"1 dan {FRIEND_MAX_PHOTOS} tagacha rasm yuborishingiz mumkin. "
                "Birinchi rasm asosiy bo'ladi.\n\n"
                "_Rasmni galereya iconi orqali yuboring (skrepka emas)._",
                reply_markup=kb_photo_step(0),
                parse_mode="Markdown",
            )
            return

        if data == "friends_bio_ai":
            setup = context.user_data.get("friends_setup", {})
            data_dict = setup.get("data", {})
            await query.edit_message_text("✨ Bio yozyapman...", parse_mode="Markdown")
            try:
                bio = await write_bio(data_dict, lang)
            except Exception as e:
                logger.error(f"AI bio failed: {e}")
                bio = ""
            data_dict["bio"] = bio[:FRIEND_BIO_MAX_LENGTH]
            setup["data"] = data_dict
            setup["step"] = "photos"
            context.user_data["friends_setup"] = setup
            preview = bio if bio else "_Bio yaratib bo'lmadi, davom etamiz._"
            await query.edit_message_text(
                f"✨ *Sizning bio:*\n\n_{preview}_\n\n"
                f"📸 Endi 1 dan {FRIEND_MAX_PHOTOS} tagacha rasm yuboring "
                "(birinchi rasm asosiy bo'ladi):",
                reply_markup=kb_photo_step(0),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard / edit photos: done / skip / clear ──────
        if data == "friends_photos_skip":
            # Skip only valid in initial setup, not in edit-photos flow
            if context.user_data.get("friends_edit_photos_state"):
                # In edit mode, "skip" doesn't make sense — treat as done
                await _finalize_photos_edit(update, context)
            else:
                await _finalize_friend_setup(update, context, photo_file_ids=[])
            return

        if data == "friends_photos_done":
            # Branch on which flow we're in
            if context.user_data.get("friends_edit_photos_state"):
                await _finalize_photos_edit(update, context)
            else:
                setup = context.user_data.get("friends_setup", {})
                photos = setup.get("data", {}).get("photo_file_ids", [])
                await _finalize_friend_setup(update, context, photo_file_ids=photos)
            return

        if data == "friends_photos_clear":
            # Clear in either flow
            if context.user_data.get("friends_edit_photos_state"):
                context.user_data["friends_edit_photos_state"] = {"photos": []}
            else:
                setup = context.user_data.get("friends_setup", {})
                data_dict = setup.setdefault("data", {})
                data_dict["photo_file_ids"] = []
                setup["data"] = data_dict
                context.user_data["friends_setup"] = setup
            await query.edit_message_text(
                f"🗑 Hammasi tozalandi.\n\n"
                f"📸 Yangidan 1 dan {FRIEND_MAX_PHOTOS} tagacha rasm yuboring:",
                reply_markup=kb_photo_step(0),
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
                "🎯 *Filtrlar*\n\n"
                "_Tanishuv bo'limida ko'rinadigan odamlarni cheklash uchun:_",
                reply_markup=kb_preferences(prefs),
                parse_mode="Markdown",
            )
            return

        if data == "friends_pref_gender":
            await query.edit_message_text(
                "👤 *Kimni izlayapsiz?*",
                reply_markup=kb_pref_gender_select(),
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
                "🎯 *Filtrlar*",
                reply_markup=kb_preferences(prefs),
                parse_mode="Markdown",
            )
            return

        if data == "friends_pref_age":
            context.user_data["friends_pref_age"] = True
            await query.edit_message_text(
                "🎂 *Yosh oralig'ini kiriting*\n\n"
                "Format: `min-max`\n"
                "Misol: `20-30` yoki `18-100`",
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
                "🎯 *Filtrlar*",
                reply_markup=kb_preferences(prefs),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit":
            # Show sub-menu: edit photos only, or rewrite full anketa
            await query.edit_message_text(
                "✏️ *Tahrirlash*\n\nNimani o'zgartirmoqchisiz?",
                reply_markup=kb_edit_choices(lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit_photos":
            # Start a focused photo-edit flow that ONLY replaces the photo set,
            # preserving everything else.
            context.user_data["friends_edit_photos_state"] = {"photos": []}
            context.user_data.pop("friends_setup", None)
            await query.edit_message_text(
                f"📸 *Rasmlarni o'zgartirish*\n\n"
                f"Yangi rasmlaringizni yuboring (1 dan {FRIEND_MAX_PHOTOS} tagacha).\n"
                "Eski rasmlar yangilari bilan to'liq almashtiriladi.",
                reply_markup=kb_photo_step(0),
                parse_mode="Markdown",
            )
            return

        if data == "friends_edit_full":
            # Old behavior — wipe and re-run wizard
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
            await query.answer("Anketa yashirildi", show_alert=False)
            profile = await get_friend_profile(user.id)
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_show":
            await reactivate_friend_profile(user.id)
            await query.answer("Anketa ko'rinmoqda", show_alert=False)
            profile = await get_friend_profile(user.id)
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_browse":
            # Daily quota check
            if not await is_premium_active(user.id):
                usage = await get_friend_daily_usage(user.id)
                if usage["likes_given"] >= FREE_DAILY_LIKES:
                    await query.edit_message_text(
                        f"🚫 *Bugungi like chegarasi tugadi* ({FREE_DAILY_LIKES} ta).\n\n"
                        "💎 *Premium*'ga o'tib cheksiz like bering!",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("💎 Premium", callback_data="menu_premium")],
                            [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
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
            await query.answer("Foydalanuvchi bloklandi", show_alert=False)
            context.user_data.pop("browsing_candidate_id", None)
            my_profile = await get_friend_profile(user.id)
            await _show_next_profile(update, context, my_profile, lang, edit_query=query)
            return

        if data.startswith("friends_icebreakers_"):
            try:
                other_id = int(data.replace("friends_icebreakers_", ""))
            except ValueError:
                return
            await query.answer("AI savollarni tayyorlayapti...", show_alert=False)
            other = await get_friend_profile(other_id)
            if not other:
                return
            try:
                qs = await generate_icebreakers(profile, other, lang)
            except Exception as e:
                logger.error(f"Icebreakers gen failed: {e}")
                qs = []
            text = "💡 *Suhbat boshlovchi savollar:*\n\n"
            text += "\n\n".join(f"• _{q}_" for q in qs) if qs else "Texnik xatolik."
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "💬 Telegram'da yozish",
                        url=f"tg://user?id={other_id}",
                    )],
                    [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
                ]),
                parse_mode="Markdown",
            )
            return

        # ── Photo verification ─────────────────────────────────────
        if data == "friends_verify_start":
            if not profile.get("photo_file_id"):
                await query.edit_message_text(
                    "❌ Avval profilingizga rasm qo'shing — keyin tasdiqlay olasiz.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back"),
                    ]]),
                )
                return
            context.user_data["friends_verify"] = True
            await query.edit_message_text(
                "🛡 *Anketani tasdiqlash*\n\n"
                "Hozir bizga *yangi selfie* yuboring — yuzingizni aniq ko'rsatadigan, "
                "yorug' joyda olingan rasm.\n\n"
                "AI selfini sizning anketa rasmingiz bilan solishtirib, "
                "✅ *Tasdiqlangan* belgisini beradi.\n\n"
                "_(Tasdiqlangan profillar 3x ko'proq match oladi.)_",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Bekor qilish", callback_data="friends_back"),
                ]]),
                parse_mode="Markdown",
            )
            return

        if data == "friends_verified_info":
            await query.answer(
                "✅ Sizning anketangiz tasdiqlangan! 3x ko'proq ko'rinadi.",
                show_alert=True,
            )
            return

        # legacy
        if data == "friends_waitlist":
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

    except Exception as e:
        logger.error(f"Error in friends_callback: {e}")
        try:
            await query.edit_message_text("Xatolik yuz berdi.")
        except Exception:
            pass


async def friends_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text inputs during the friend setup wizard or preferences edit."""
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()

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
                "❌ Format noto'g'ri. Misol: `20-30` (18-100 oralig'ida)",
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
            "✅ Yosh oralig'i yangilandi.",
            reply_markup=kb_preferences(prefs),
        )
        return

    setup = context.user_data.get("friends_setup")
    if not setup:
        return

    step = setup.get("step")
    data = setup.setdefault("data", {})

    if step == "name":
        if len(text) < 2 or len(text) > 50:
            await message.reply_text("❌ Ism 2-50 ta belgi bo'lishi kerak.")
            return
        data["display_name"] = text
        setup["step"] = "age"
        await message.reply_text(
            "🎂 *Yoshingiz?*\n\nFaqat raqam yozing (masalan: `22`).\n"
            f"_Bot {FRIEND_MIN_AGE}+ yosh foydalanuvchilar uchun._",
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
                f"❌ Yoshi {FRIEND_MIN_AGE} dan {FRIEND_MAX_AGE} gacha bo'lishi kerak."
            )
            return
        data["age"] = age
        setup["step"] = "looking_for"
        await message.reply_text(
            "🎯 *Nima izlayapsiz?*",
            reply_markup=kb_looking_for(),
            parse_mode="Markdown",
        )
        return

    if step == "city":
        if len(text) < 2 or len(text) > 100:
            await message.reply_text("❌ Shahar nomi 2-100 ta belgi bo'lishi kerak.")
            return
        data["city"] = text
        setup["step"] = "interests"
        data.setdefault("interests", [])
        await message.reply_text(
            "✨ *Qiziqishlaringizni tanlang*\n\n"
            f"Kamida {FRIEND_MIN_INTERESTS} ta, ko'pi bilan {FRIEND_MAX_INTERESTS} ta:",
            reply_markup=kb_interests([]),
            parse_mode="Markdown",
        )
        return

    if step == "bio":
        bio = "" if text in ("-", "—", "skip") else text
        if len(bio) > FRIEND_BIO_MAX_LENGTH:
            await message.reply_text(
                f"❌ Bio juda uzun ({len(bio)} ta belgi). "
                f"Maksimum {FRIEND_BIO_MAX_LENGTH} ta."
            )
            return
        data["bio"] = bio
        setup["step"] = "photos"
        data.setdefault("photo_file_ids", [])
        await message.reply_text(
            f"📸 *Profilingizga rasm qo'shing*\n\n"
            f"1 dan {FRIEND_MAX_PHOTOS} tagacha rasm yuborishingiz mumkin "
            "(birinchi rasm asosiy bo'ladi).",
            reply_markup=kb_photo_step(0),
            parse_mode="Markdown",
        )
        return


async def _resolve_to_photo_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message,
) -> Optional[str]:
    """
    Resolve any image submission (photo OR image-document) to a Telegram
    *photo* file_id we can later send via send_photo().
    """
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
            await message.reply_text(
                "❌ Rasmni qayta ishlashda xatolik. Iltimos, *fayl* sifatida emas, "
                "*rasm* sifatida qaytadan yuboring (skrepka emas, kamera/galereya iconi).",
                parse_mode="Markdown",
            )
            return None

    return None


def _check_photo_quality(message) -> Optional[str]:
    """
    Run cheap pre-checks (size, dimensions) before paying for moderation API.
    Returns a user-facing error string, or None if the photo passes.
    """
    file_size = None
    width = None
    height = None

    if message.photo:
        # Use the largest size
        largest = message.photo[-1]
        file_size = largest.file_size
        width = largest.width
        height = largest.height
    elif message.document:
        file_size = message.document.file_size
        # Documents don't reliably expose dimensions; we skip that check
        if message.document.thumbnail:
            width = message.document.thumbnail.width
            height = message.document.thumbnail.height

    if file_size is not None:
        if file_size < FRIEND_PHOTO_MIN_FILE_SIZE:
            return (
                "📐 Rasm juda kichik (sifati past). "
                "Yaxshiroq rasm yuboring."
            )
        if file_size > FRIEND_PHOTO_MAX_FILE_SIZE:
            return (
                "📐 Rasm juda katta (8 MB dan ortiq). "
                "Kichikroq rasm yuboring."
            )

    if width and height:
        if min(width, height) < FRIEND_PHOTO_MIN_DIMENSION:
            return (
                f"📐 Rasm o'lchami juda kichik ({width}×{height}px). "
                f"Eng kami {FRIEND_PHOTO_MIN_DIMENSION}px kerak."
            )

    return None


async def _moderate_photo_bytes(file_id: str, context) -> tuple:
    """Download a photo by file_id and moderate it.

    Returns (approved: bool, reason: str).
    """
    try:
        f = await context.bot.get_file(file_id)
        photo_bytes = await f.download_as_bytearray()
        result = await moderate_image(bytes(photo_bytes))
        return result.approved, result.reason
    except Exception as e:
        logger.error(f"Moderation download failed: {e}")
        # Fail-open
        return True, ""


async def friends_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive a photo: either anketa photo OR verification selfie OR edit-photo flow."""
    setup = context.user_data.get("friends_setup")
    is_verifying = context.user_data.get("friends_verify")
    is_editing_photos = context.user_data.get("friends_edit_photos_state")

    message = update.message
    if not message:
        return

    # Only run if user is in a state expecting a photo
    in_photo_step = bool(setup and setup.get("step") == "photos")
    if not (is_verifying or in_photo_step or is_editing_photos):
        return

    # Cheap pre-checks
    quality_error = _check_photo_quality(message)
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

    # AI content moderation (skips if no API key)
    await message.chat.send_action("typing")
    approved, reason = await _moderate_photo_bytes(photo_file_id, context)
    if not approved:
        text = "❌ *Bu rasmni qabul qila olmayman.*"
        if reason:
            text += f"\n\n_{reason}_"
        text += "\n\nIltimos, boshqa rasm yuboring."
        await message.reply_text(text, parse_mode="Markdown")
        return

    # ── Editing photos only (post-anketa) ────────────────────────
    if is_editing_photos:
        photos = is_editing_photos.get("photos", [])
        if len(photos) >= FRIEND_MAX_PHOTOS:
            await message.reply_text(
                f"❌ Maksimum {FRIEND_MAX_PHOTOS} ta rasm. "
                "Tasdiqlash tugmasini bosing yoki boshqatdan boshlang."
            )
            return
        photos.append(photo_file_id)
        is_editing_photos["photos"] = photos
        context.user_data["friends_edit_photos_state"] = is_editing_photos
        await message.reply_text(
            f"✅ {len(photos)}/{FRIEND_MAX_PHOTOS} rasm qabul qilindi.\n\n"
            "Yana yuborishingiz mumkin yoki tasdiqlang:",
            reply_markup=kb_photo_step(len(photos)),
        )
        return

    # ── Anketa photo accumulator (multi-photo) ───────────────────
    if in_photo_step:
        data = setup.setdefault("data", {})
        photos = data.setdefault("photo_file_ids", [])
        if len(photos) >= FRIEND_MAX_PHOTOS:
            await message.reply_text(
                f"❌ Maksimum {FRIEND_MAX_PHOTOS} ta rasm. "
                "Tasdiqlash tugmasini bosing yoki boshqatdan boshlang."
            )
            return
        photos.append(photo_file_id)
        data["photo_file_ids"] = photos
        setup["data"] = data
        context.user_data["friends_setup"] = setup
        await message.reply_text(
            f"✅ {len(photos)}/{FRIEND_MAX_PHOTOS} rasm qabul qilindi.\n\n"
            "Yana yuborishingiz mumkin yoki tasdiqlang:",
            reply_markup=kb_photo_step(len(photos)),
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
        profile = await get_friend_profile(user.id)
        first_photo = _get_first_photo(profile) if profile else None
        if not first_photo:
            await chat.send_message("❌ Avval profil rasmini qo'shing.")
            context.user_data.pop("friends_verify", None)
            return

        saved_file = await context.bot.get_file(first_photo)
        saved_bytes = await saved_file.download_as_bytearray()

        selfie_file = await context.bot.get_file(photo_file_id)
        selfie_bytes = await selfie_file.download_as_bytearray()

        await chat.send_message("🔍 AI tasdiqlamoqda...")
        verified, note = await verify_photos(bytes(saved_bytes), bytes(selfie_bytes))
        await upsert_photo_verification(user.id, verified, note)

        context.user_data.pop("friends_verify", None)

        if verified:
            await chat.send_message(
                f"✅ *Tasdiqlandi!*\n\n_{note}_\n\n"
                "Endi anketangizda \"✅ Tasdiqlangan\" belgisi paydo bo'ladi va "
                "siz 3x ko'proq ko'rinasiz.",
                parse_mode="Markdown",
            )
        else:
            await chat.send_message(
                f"❌ *Tasdiqlanmadi.*\n\n_{note}_\n\n"
                "Yorug' joyda yangi selfie bilan qaytadan urinib ko'ring.",
                parse_mode="Markdown",
            )

        lang = await user_service.get_user_language(user.id)
        profile = await get_friend_profile(user.id)
        await _show_friends_main(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Verification flow error: {e}")
        await chat.send_message("Tasdiqlashda xatolik. Qaytadan urinib ko'ring.")


async def _finalize_friend_setup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_file_ids: Optional[list] = None,
) -> None:
    """Save the assembled profile and show the dashboard."""
    user = update.effective_user
    setup = context.user_data.get("friends_setup", {})
    data = setup.get("data", {})

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
        await update.effective_chat.send_message(
            "❌ Anketani saqlashda xatolik. Iltimos, qaytadan urinib ko'ring."
        )
        return

    context.user_data.pop("friends_setup", None)
    lang = await user_service.get_user_language(user.id)
    profile = await get_friend_profile(user.id)

    await update.effective_chat.send_message(
        "🎉 *Anketangiz tayyor!*\n\n"
        "Endi siz boshqalarni ko'rasiz va ular ham sizni topadi.\n"
        "_Maslahat: anketani tasdiqlasangiz 3x ko'proq match olasiz._",
        parse_mode="Markdown",
    )
    await _show_friends_main(update, context, profile, lang, chat=update.effective_chat)


async def _finalize_photos_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Save photos-only edit and show the dashboard."""
    user = update.effective_user
    state = context.user_data.get("friends_edit_photos_state", {})
    photos = state.get("photos", [])

    try:
        await update_friend_photos(user.id, photos)
    except Exception as e:
        logger.error(f"Error updating photos: {e}")
        await update.effective_chat.send_message(
            "❌ Rasmlarni saqlashda xatolik. Qaytadan urinib ko'ring."
        )
        return

    context.user_data.pop("friends_edit_photos_state", None)
    lang = await user_service.get_user_language(user.id)
    profile = await get_friend_profile(user.id)
    await update.effective_chat.send_message(
        f"✅ *{len(photos)} ta rasm saqlandi!*",
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

    # Apply preferences (filters)
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

    # Fallback: drop city filter if nothing found
    if not candidate and same_city_only:
        candidate = await get_next_browse_profile(
            viewer_id=user_id,
            looking_for=looking,
            target_gender=target_gender,
            min_age=min_age,
            max_age=max_age,
        )

    if not candidate:
        text = (
            "🔍 *Hozircha mos anketalar yo'q*\n\n"
            "Filtrlarni kengaytirib ko'ring yoki keyinroq qaytib tekshiring."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Filtrlar", callback_data="friends_prefs")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
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

    # Add verified badge if applicable
    cand_verification = await get_photo_verification(candidate["user_id"])
    is_verified = bool(cand_verification and cand_verification.get("is_verified"))

    photos = _get_all_photos(candidate)
    photo_count = len(photos)

    card_text = _format_profile_card(candidate, verified=is_verified, photo_count=photo_count)
    kb = kb_browse_actions(candidate["user_id"])

    if photos:
        if edit_query:
            try:
                await edit_query.delete_message()
            except Exception:
                pass
        # Show first (main) photo with the action keyboard
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
        await update.effective_chat.send_message(
            card_text, reply_markup=kb, parse_mode="Markdown",
        )


def _format_profile_card(profile: dict, verified: bool = False, photo_count: int = 0) -> str:
    """Render a profile card."""
    name = profile.get("display_name", "—")
    age = profile.get("age", "")
    city = profile.get("city", "")
    looking = FRIEND_LOOKING_LABELS_UZ.get(profile.get("looking_for", ""), "—")
    interests = profile.get("interests") or []
    interests_str = " · ".join(
        FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in interests[:6]
    )
    bio = profile.get("bio") or ""

    badge = " ✅" if verified else ""
    parts = [f"✨ *{name}, {age}*{badge}"]
    if city:
        parts.append(f"📍 {city}")
    parts.append(f"🎯 {looking}")
    if photo_count > 1:
        parts.append(f"📸 _{photo_count} ta rasm_")
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
    candidate_id = context.user_data.get("browsing_candidate_id")
    if not candidate_id:
        my_profile = await get_friend_profile(user.id)
        lang = await user_service.get_user_language(user.id)
        await _show_next_profile(update, context, my_profile, lang, edit_query=query)
        return

    # Double-check daily quota for likes
    if is_like and not await is_premium_active(user.id):
        usage = await get_friend_daily_usage(user.id)
        if usage["likes_given"] >= FREE_DAILY_LIKES:
            await query.answer(
                f"Bugungi {FREE_DAILY_LIKES} like chegarasi tugadi. Premium'ga o'ting.",
                show_alert=True,
            )
            return

    # Block check (defensive)
    if await is_blocked(user.id, candidate_id):
        context.user_data.pop("browsing_candidate_id", None)
        my_profile = await get_friend_profile(user.id)
        lang = await user_service.get_user_language(user.id)
        await _show_next_profile(update, context, my_profile, lang, edit_query=query)
        return

    is_match = await record_friend_reaction(user.id, candidate_id, is_like)
    context.user_data.pop("browsing_candidate_id", None)
    if is_like:
        await increment_friend_likes(user.id)

    if is_match and is_like:
        candidate = await get_friend_profile(candidate_id)
        text = (
            f"🎉 *Match!*\n\n"
            f"Siz va {candidate.get('display_name', '—')} bir-biringizni yoqtirdingiz!\n\n"
            f"💬 To'g'ridan-to'g'ri Telegram'da yozishingiz mumkin yoki AI'dan "
            f"suhbat boshlovchi savollarni so'rang."
        )
        try:
            await query.delete_message()
        except Exception:
            pass
        await update.effective_chat.send_message(
            text,
            reply_markup=kb_match_actions(candidate_id),
            parse_mode="Markdown",
        )
        return

    my_profile = await get_friend_profile(user.id)
    lang = await user_service.get_user_language(user.id)
    await _show_next_profile(update, context, my_profile, lang, edit_query=query)


# ──────────────────────── My profile / Matches / Likes views ────────────────────────

async def _show_my_profile(query, profile: dict, user_id: int, lang: str) -> None:
    """Show the user their own profile. Sends a media-group when there are
    multiple photos so all of them are visible at once."""
    from telegram import InputMediaPhoto

    verification = await get_photo_verification(user_id)
    is_verified = bool(verification and verification.get("is_verified"))
    photos = _get_all_photos(profile)
    text = "👤 *Mening anketam:*\n\n" + _format_profile_card(
        profile, verified=is_verified, photo_count=len(photos),
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Rasmlarni o'zgartirish", callback_data="friends_edit_photos")],
        [InlineKeyboardButton("✏️ To'liq tahrirlash", callback_data="friends_edit_full")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
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
        # Send album of all photos first (no caption — short captions can be
        # cut off in albums and Telegram limits 1 caption per group)
        media = [InputMediaPhoto(media=p) for p in photos[:10]]
        try:
            await chat.send_media_group(media=media)
        except Exception as e:
            logger.error(f"send_media_group failed: {e}")
        # Then send the card text + action buttons as a separate message
        await chat.send_message(text, reply_markup=kb, parse_mode="Markdown")
    else:
        # Single photo — caption + buttons together
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
            "💌 *Match'lar*\n\n"
            "Hozircha match'lar yo'q. Tanishuv bo'limida boshqa anketalarni ko'ring!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💝 Tanishuv boshlash", callback_data="friends_browse")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    lines = ["💌 *Sizning match'laringiz:*\n"]
    rows = []
    for m in matches[:10]:
        lines.append(f"• *{m['display_name']}*, {m['age']} — _{m.get('city', '—')}_")
        rows.append([InlineKeyboardButton(
            f"💬 {m['display_name']}",
            url=f"tg://user?id={m['user_id']}",
        )])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")])
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
            "💖 *Sizni yoqtirganlar*\n\n"
            "Hozircha hech kim yoqtirmagan. Anketani sifatliroq qiling, "
            "rasmni tasdiqlang — match'lar oshadi!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    if not is_pro:
        await query.edit_message_text(
            f"💖 *Sizni yoqtirganlar: {count}*\n\n"
            "Kim ekanligini ko'rish va ularga match qaytarish uchun "
            "💎 *Premium*'ga o'ting.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium olish", callback_data="menu_premium")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
            ]),
            parse_mode="Markdown",
        )
        return

    # Premium: show actual profiles
    profiles = await get_users_who_liked_me(user_id)
    lines = [f"💖 *Sizni yoqtirganlar: {count}*\n"]
    for p in profiles[:10]:
        lines.append(
            f"• *{p['display_name']}*, {p['age']} — _{p.get('city', '—')}_"
        )
    if not profiles:
        lines.append("_Yangilash uchun keyinroq qayting._")
    rows = [[InlineKeyboardButton("💝 Tanishuv boshlash", callback_data="friends_browse")]]
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")])
    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )
