"""
Reminder scheduler
"""
import asyncio
from datetime import datetime
from telegram import Bot
import logging

from mindmate.core.config import settings
from mindmate.db.queries import get_pending_reminders, mark_reminder_sent
from mindmate.reminders.parser import get_next_occurrence
from mindmate.i18n import t

logger = logging.getLogger(__name__)

# Global scheduler task
_scheduler_task = None


async def check_and_send_reminders(bot: Bot) -> None:
    """
    Check for pending reminders and send them.

    Args:
        bot: Telegram Bot instance
    """
    try:
        current_time = datetime.now()
        pending = await get_pending_reminders(current_time)

        for reminder in pending:
            try:
                user_id = reminder['user_id']
                text = reminder['text']
                reminder_id = reminder['id']
                repeat_type = reminder.get('repeat_type', 'once')

                # Send reminder to user
                message = f"⏰ Reminder: {text}"
                await bot.send_message(chat_id=user_id, text=message)

                # Mark as sent
                await mark_reminder_sent(reminder_id)

                logger.info(f"Sent reminder {reminder_id} to user {user_id}")

                # If it's a repeating reminder, create next occurrence
                # (In a real implementation, you'd create a new reminder entry)
                if repeat_type != 'once':
                    logger.info(f"Repeating reminder {reminder_id} is {repeat_type}")
                    # TODO: Create new reminder for next occurrence

            except Exception as e:
                logger.error(f"Error sending reminder {reminder.get('id')}: {e}")

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")


async def reminder_scheduler_loop(bot: Bot) -> None:
    """
    Main scheduler loop that runs continuously.

    Args:
        bot: Telegram Bot instance
    """
    logger.info("Reminder scheduler started")

    while True:
        try:
            await check_and_send_reminders(bot)
            # Wait for the configured interval
            await asyncio.sleep(settings.REMINDER_CHECK_INTERVAL)

        except asyncio.CancelledError:
            logger.info("Reminder scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Error in reminder scheduler loop: {e}")
            # Wait a bit before retrying to avoid rapid error loops
            await asyncio.sleep(60)


async def start_scheduler(bot: Bot) -> None:
    """
    Start the reminder scheduler.

    Args:
        bot: Telegram Bot instance
    """
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
