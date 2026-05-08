"""
Friend-finding feature — full MVP.

Flow:
1. /friends or "💝 Do'st topish" button
2. If no profile → setup wizard (name, age, gender, city, looking_for, interests, bio, photo)
3. Otherwise → main friends menu (Browse, My Profile, Matches, Settings)

Designed to feel premium and intentional — anketa is short but expressive,
browsing is paced (not infinite swipe), matches lead directly to Telegram chat.
"""
import logging
from typing import Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    get_friend_profile,
    upsert_friend_profile,
    deactivate_friend_profile,
    reactivate_friend_profile,
    delete_friend_profile,
    get_next_browse_profile,
    record_friend_reaction,
    get_friend_matches,
    count_friend_likes_received,
    is_premium_active,
)
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
)

logger = logging.getLogger(__name__)


# ──────────────────────── Keyboards ────────────────────────

def kb_friends_main(profile: dict, lang: str = "uz") -> InlineKeyboardMarkup:
    """Main friends menu when profile exists."""
    is_active = profile.get("is_active", True)
    visibility_btn = (
        InlineKeyboardButton("🙈 Anketani yashirish", callback_data="friends_hide")
        if is_active else
        InlineKeyboardButton("👁 Anketani ko'rsat", callback_data="friends_show")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💝 Tanishuv boshlash", callback_data="friends_browse")],
        [
            InlineKeyboardButton("✨ Mening anketam", callback_data="friends_myprofile"),
            InlineKeyboardButton("💌 Match'lar", callback_data="friends_matches"),
        ],
        [
            InlineKeyboardButton("⚙️ Anketani tahrirlash", callback_data="friends_edit"),
            visibility_btn,
        ],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ])


def kb_browse_actions() -> InlineKeyboardMarkup:
    """Like/Pass buttons during browsing."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ O'tib ketish", callback_data="friends_pass"),
            InlineKeyboardButton("❤️ Yoqdi", callback_data="friends_like"),
        ],
        [InlineKeyboardButton("⏸ Tanishuvni to'xtatish", callback_data="friends_back")],
    ])


def kb_match_actions(match_user_id: int) -> InlineKeyboardMarkup:
    """When a match is created, offer to open chat."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💬 Telegram'da yozish",
            url=f"tg://user?id={match_user_id}",
        )],
        [InlineKeyboardButton("➡️ Tanishuvni davom ettirish", callback_data="friends_browse")],
    ])


def kb_looking_for() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(FRIEND_LOOKING_LABELS_UZ[lf], callback_data=f"friends_lf_{lf}")]
        for lf in FRIEND_LOOKING_OPTIONS
    ])


def kb_gender() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(FRIEND_GENDER_LABELS_UZ[g], callback_data=f"friends_g_{g}")]
        for g in FRIEND_GENDER_OPTIONS
    ]
    rows.append([InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="friends_g_skip")])
    return InlineKeyboardMarkup(rows)


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


def kb_photo_step() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Rasmsiz davom etish", callback_data="friends_photo_skip")],
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
    likes_text = (
        f"💝 Sizni yoqtirganlar: *{likes_received}*"
        if await is_premium_active(profile["user_id"])
        else f"💝 Sizni yoqtirganlar: *{likes_received}* (Premium'da kim ekanligi)"
    )

    text = (
        f"💝 *Do'st topish*\n\n"
        f"👤 {name}, {age}\n"
        f"🎯 {looking}\n"
        f"{visibility}\n\n"
        f"{likes_text}\n\n"
        f"_Bugun yangi tanishuv?_"
    )

    kb = kb_friends_main(profile, lang)
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

        # ── Setup wizard: looking_for selection ────────────────────
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

        # ── Setup wizard: gender ───────────────────────────────────
        if data.startswith("friends_g_"):
            tag = data.replace("friends_g_", "")
            setup = context.user_data.get("friends_setup", {})
            if tag != "skip":
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

        # ── Setup wizard: interests multi-select ───────────────────
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
                    "1-3 jumla — kim ekanligingiz, nimaga qiziqasiz, qanday "
                    "odamni qidirayapsiz.\n\n"
                    f"_Maksimum {FRIEND_BIO_MAX_LENGTH} ta belgi. "
                    "Bo'sh qoldirsangiz \"-\" deb yozing._",
                    parse_mode="Markdown",
                )
                return

            # Toggle interest
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

        # ── Setup wizard: skip photo ───────────────────────────────
        if data == "friends_photo_skip":
            await _finalize_friend_setup(update, context, photo_file_id=None)
            return

        # ── Main menu actions ──────────────────────────────────────
        profile = await get_friend_profile(user.id)
        if not profile:
            await friends_handler(update, context)
            return

        if data == "menu_friends" or data == "friends_back":
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_myprofile":
            await _show_my_profile(query, profile, lang)
            return

        if data == "friends_matches":
            await _show_matches(query, user.id, lang)
            return

        if data == "friends_edit":
            await delete_friend_profile(user.id)
            context.user_data.pop("friends_setup", None)
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
            await _show_next_profile(update, context, profile, lang, edit_query=query)
            return

        if data == "friends_like":
            await _react(update, context, is_like=True)
            return

        if data == "friends_pass":
            await _react(update, context, is_like=False)
            return

        if data == "friends_waitlist":
            # Legacy callback (from old teaser) — just open friends now
            await _show_friends_main(update, context, profile, lang, edit_query=query)
            return

    except Exception as e:
        logger.error(f"Error in friends_callback: {e}")
        try:
            await query.edit_message_text("Xatolik yuz berdi.")
        except Exception:
            pass


async def friends_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text inputs during the friend setup wizard."""
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    setup = context.user_data.get("friends_setup")
    if not setup:
        return

    text = message.text.strip()
    step = setup.get("step")
    data = setup.setdefault("data", {})

    if step == "name":
        if len(text) < 2 or len(text) > 50:
            await message.reply_text("❌ Ism 2-50 ta belgi bo'lishi kerak.")
            return
        data["display_name"] = text
        setup["step"] = "age"
        await message.reply_text(
            "🎂 *Yoshingiz?*\n\n"
            "Iltimos, faqat raqam yozing (masalan: `22`).\n"
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
        setup["step"] = "photo"
        await message.reply_text(
            "📸 *Profilingizga rasm qo'shing*\n\n"
            "Bitta rasm yuboring (yoki rasmsiz davom eting).\n"
            "_Yaxshi rasm = ko'proq tanishuv!_",
            reply_markup=kb_photo_step(),
            parse_mode="Markdown",
        )
        return


async def friends_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive a photo during the photo step of the wizard."""
    setup = context.user_data.get("friends_setup")
    if not setup or setup.get("step") != "photo":
        return

    message = update.message
    if not message.photo:
        return

    # Largest photo is the last entry in the photos array
    photo_file_id = message.photo[-1].file_id
    await _finalize_friend_setup(update, context, photo_file_id=photo_file_id)


async def _finalize_friend_setup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_file_id: Optional[str],
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
            photo_file_id=photo_file_id,
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
        "Endi siz boshqa foydalanuvchilarni ko'rib, ular ham sizni ko'ra oladi. "
        "Boshlaymizmi?",
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

    candidate = await get_next_browse_profile(
        viewer_id=user_id,
        looking_for=looking,
        same_city=city,
    )

    if not candidate:
        # Fallback: drop city filter
        candidate = await get_next_browse_profile(
            viewer_id=user_id,
            looking_for=looking,
        )

    if not candidate:
        text = (
            "🔍 *Hozircha mos anketalar yo'q*\n\n"
            "Yangi foydalanuvchilar qo'shilganda sizga aytaman. "
            "Vaqti-vaqti bilan qaytib tekshiring!"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back"),
        ]])
        if edit_query:
            try:
                await edit_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
                return
            except Exception:
                pass
        await update.effective_chat.send_message(text, reply_markup=kb, parse_mode="Markdown")
        return

    # Save which candidate we're showing so the like/pass buttons know who
    context.user_data["browsing_candidate_id"] = candidate["user_id"]

    card_text = _format_profile_card(candidate)

    if candidate.get("photo_file_id"):
        # Photo card — delete previous message and send fresh
        if edit_query:
            try:
                await edit_query.delete_message()
            except Exception:
                pass
        await update.effective_chat.send_photo(
            photo=candidate["photo_file_id"],
            caption=card_text,
            reply_markup=kb_browse_actions(),
            parse_mode="Markdown",
        )
    else:
        if edit_query:
            try:
                await edit_query.edit_message_text(
                    card_text,
                    reply_markup=kb_browse_actions(),
                    parse_mode="Markdown",
                )
                return
            except Exception:
                pass
        await update.effective_chat.send_message(
            card_text,
            reply_markup=kb_browse_actions(),
            parse_mode="Markdown",
        )


def _format_profile_card(profile: dict) -> str:
    """Render a profile as a nice card."""
    name = profile.get("display_name", "—")
    age = profile.get("age", "")
    city = profile.get("city", "")
    looking = FRIEND_LOOKING_LABELS_UZ.get(profile.get("looking_for", ""), "—")
    interests = profile.get("interests") or []
    interests_str = " · ".join(
        FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in interests[:6]
    )
    bio = profile.get("bio") or ""

    parts = [f"✨ *{name}, {age}*"]
    if city:
        parts.append(f"📍 {city}")
    parts.append(f"🎯 {looking}")
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
    """Record a like/pass and either show match dialog or continue browsing."""
    query = update.callback_query
    user = query.from_user
    candidate_id = context.user_data.get("browsing_candidate_id")
    if not candidate_id:
        # Stale state — restart browse
        my_profile = await get_friend_profile(user.id)
        lang = await user_service.get_user_language(user.id)
        await _show_next_profile(update, context, my_profile, lang, edit_query=query)
        return

    is_match = await record_friend_reaction(user.id, candidate_id, is_like)
    context.user_data.pop("browsing_candidate_id", None)

    if is_match and is_like:
        # Show match celebration
        candidate = await get_friend_profile(candidate_id)
        text = (
            f"🎉 *Match!*\n\n"
            f"Siz va {candidate.get('display_name', '—')} bir-biringizni yoqtirdingiz!\n\n"
            f"💬 Endi to'g'ridan-to'g'ri Telegram'da yozishingiz mumkin."
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

    # Otherwise continue browsing
    my_profile = await get_friend_profile(user.id)
    lang = await user_service.get_user_language(user.id)
    await _show_next_profile(update, context, my_profile, lang, edit_query=query)


# ──────────────────────── My profile / Matches views ────────────────────────

async def _show_my_profile(query, profile: dict, lang: str) -> None:
    """Show the user their own profile card."""
    text = "👤 *Mening anketam:*\n\n" + _format_profile_card(profile)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Tahrirlash", callback_data="friends_edit")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="friends_back")],
    ])
    if profile.get("photo_file_id"):
        try:
            await query.delete_message()
        except Exception:
            pass
        await query.message.chat.send_photo(
            photo=profile["photo_file_id"],
            caption=text,
            reply_markup=kb,
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")


async def _show_matches(query, user_id: int, lang: str) -> None:
    """Show the user's matches list."""
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
        lines.append(
            f"• *{m['display_name']}*, {m['age']} — _{m.get('city', '—')}_"
        )
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
