"""
Reminder scheduler
"""
import asyncio
import logging
from datetime import datetime, timedelta

from telegram import Bot

from mindmate.core.config import settings
from mindmate.db.queries import (
    get_pending_reminders,
    mark_reminder_sent,
    update_reminder_time,
)

logger = logging.getLogger(__name__)

# Global scheduler task
_scheduler_task = None


def _next_occurrence(current: datetime, repeat_type: str) -> datetime:
    """Compute the next firing time for a repeating reminder."""
    if repeat_type == "daily":
        return current + timedelta(days=1)
    if repeat_type == "weekly":
        return current + timedelta(weeks=1)
    if repeat_type == "monthly":
        # Approximate a month as 30 days (sufficient for casual reminders)
        return current + timedelta(days=30)
    return current  # 'once' or unknown — caller should not use


async def check_and_send_reminders(bot: Bot) -> None:
    """Check for pending reminders and send them. Reschedule repeats."""
    try:
        current_time = datetime.now()
        pending = await get_pending_reminders(current_time)

        for reminder in pending:
            try:
                user_id = reminder["user_id"]
                text = reminder["text"]
                reminder_id = reminder["id"]
                repeat_type = reminder.get("repeat_type", "once")
                reminder_time = reminder["reminder_time"]

                # Send reminder to user
                message = f"⏰ Reminder: {text}"
                await bot.send_message(chat_id=user_id, text=message)

                if repeat_type and repeat_type != "once":
                    # Reschedule the same row to next occurrence
                    next_time = _next_occurrence(reminder_time, repeat_type)
                    # Make sure the rescheduled time is in the future even if we
                    # missed several intervals (e.g. bot was offline)
                    while next_time <= current_time:
                        next_time = _next_occurrence(next_time, repeat_type)
                    await update_reminder_time(reminder_id, next_time)
                    logger.info(
                        f"Rescheduled repeating reminder {reminder_id} "
                        f"({repeat_type}) to {next_time.isoformat()}"
                    )
                else:
                    # One-shot reminder — mark sent so it won't fire again
                    await mark_reminder_sent(reminder_id)

                logger.info(f"Sent reminder {reminder_id} to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending reminder {reminder.get('id')}: {e}")

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
            # Backoff before retrying
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
