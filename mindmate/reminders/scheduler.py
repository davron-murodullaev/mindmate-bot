"""
Reminder scheduler
"""
import asyncio
import logging
from datetime import datetime, timedelta

from telegram import Bot
from telegram.error import Forbidden, BadRequest

from mindmate.core.config import settings
from mindmate.db.queries import (
    get_pending_reminders,
    mark_reminder_sent,
    update_reminder_time,
    update_user_active_status,
    get_user,
)

logger = logging.getLogger(__name__)

_scheduler_task = None

_REMINDER_MESSAGES = {
    "uz": "⏰ Eslatma: {text}",
    "ru": "⏰ Напоминание: {text}",
    "en": "⏰ Reminder: {text}",
}


def _next_occurrence(current: datetime, repeat_type: str) -> datetime:
    """Compute the next firing time for a repeating reminder."""
    if repeat_type == "daily":
        return current + timedelta(days=1)
    if repeat_type == "weekly":
        return current + timedelta(weeks=1)
    if repeat_type == "monthly":
        return current + timedelta(days=30)
    return current


async def check_and_send_reminders(bot: Bot) -> None:
    """Check for pending reminders and send them. Reschedule repeats."""
    try:
        current_time = datetime.now()
        pending = await get_pending_reminders(current_time)

        for reminder in pending:
            reminder_id = reminder.get("id")
            user_id = reminder["user_id"]
            try:
                text = reminder["text"]
                repeat_type = reminder.get("repeat_type", "once")
                reminder_time = reminder["reminder_time"]

                # Use user's language for the message
                user = await get_user(user_id)
                lang = (user or {}).get("language_code", "uz")
                template = _REMINDER_MESSAGES.get(lang, _REMINDER_MESSAGES["uz"])
                message = template.format(text=text)

                await bot.send_message(chat_id=user_id, text=message)

                if repeat_type and repeat_type != "once":
                    next_time = _next_occurrence(reminder_time, repeat_type)
                    while next_time <= current_time:
                        next_time = _next_occurrence(next_time, repeat_type)
                    await update_reminder_time(reminder_id, next_time)
                    logger.info(
                        f"Rescheduled reminder {reminder_id} ({repeat_type}) → {next_time.isoformat()}"
                    )
                else:
                    await mark_reminder_sent(reminder_id)

                logger.info(f"Sent reminder {reminder_id} to user {user_id}")

            except Forbidden:
                # User blocked the bot — deactivate them and mark reminder sent
                logger.warning(f"User {user_id} blocked the bot; deactivating.")
                await update_user_active_status(user_id, False)
                if reminder_id:
                    await mark_reminder_sent(reminder_id)

            except BadRequest as e:
                logger.error(f"BadRequest sending reminder {reminder_id} to {user_id}: {e}")
                if reminder_id:
                    await mark_reminder_sent(reminder_id)

            except Exception as e:
                logger.error(f"Error sending reminder {reminder_id}: {e}")

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")


async def reminder_scheduler_loop(bot: Bot) -> None:
    """Main scheduler loop that runs continuously."""
    logger.info("Reminder scheduler started")

    while True:
        try:
            await check_and_send_reminders(bot)
            await asyncio.sleep(settings.REMINDER_CHECK_INTERVAL)
        except asyncio.CancelledError:
            logger.info("Reminder scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Error in reminder scheduler loop: {e}")
            await asyncio.sleep(60)


async def start_scheduler(bot: Bot) -> None:
    """Start the reminder scheduler."""
    global _scheduler_task

    if _scheduler_task is not None and not _scheduler_task.done():
        logger.warning("Scheduler already running")
        return

    if settings.ENABLE_REMINDERS:
        _scheduler_task = asyncio.create_task(reminder_scheduler_loop(bot))
        logger.info("Reminder scheduler task created")
    else:
        logger.info("Reminders are disabled in settings")


async def stop_scheduler() -> None:
    """Stop the reminder scheduler."""
    global _scheduler_task

    if _scheduler_task is not None and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None
        logger.info("Reminder scheduler stopped")
