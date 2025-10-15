SUBJECTS = {
    "Веб": {
        "enabled": True,
        "schedule": [("tue", 14, 28)],
    },
    "Тестирование": {
        "enabled": True,
        "schedule": [("tue", 14, 28), ("fri", 8, 30)],
    },
}
QUEUE_LIFETIME_HOURS = 24
TIMEZONE = "Europe/Moscow"

from datetime import datetime
import pytz
print(datetime.now(pytz.timezone("Europe/Moscow")))