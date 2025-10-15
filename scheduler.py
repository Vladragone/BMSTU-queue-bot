from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import SUBJECTS, TIMEZONE
from typing import Callable

def setup_scheduler(start_queue_func: Callable, chat_id: int):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    for subject, info in SUBJECTS.items():
        if not info.get("enabled"):
            continue
        for day, hour, minute in info["schedule"]:
            scheduler.add_job(
                start_queue_func,
                "cron",
                day_of_week=day,
                hour=hour,
                minute=minute,
                args=[chat_id, [subject]],
            )

    scheduler.start()
    return scheduler
