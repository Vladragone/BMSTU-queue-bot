# queues.py
from typing import Dict, List

class QueueManager:
    def __init__(self):
        self.queues: Dict[str, List[str]] = {}
        self.active_subjects: List[str] = []
        self.active = False
        self.message_id = None

    def open(self, subjects: List[str]):
        """Открывает новые очереди для указанных предметов"""
        self.active = True
        self.active_subjects = subjects
        self.queues = {subj: [] for subj in subjects}

    def close(self):
        """Закрывает приём заявок"""
        self.active = False
        self.active_subjects = []

    def add_user(self, subject: str, user_name: str) -> bool:
        """Добавляет пользователя в очередь"""
        if subject not in self.active_subjects:
            return False
        queue = self.queues.setdefault(subject, [])
        if user_name in queue:
            return False
        queue.append(user_name)
        return True

    def format_text(self) -> str:
        if not self.active:
            return "❌ Очередь закрыта"

        text = "🕐 *Открыта очередь на запись!*\n"
        text += "Для записи напишите !" + " или !".join(self.active_subjects) + "\n\n"

        for subj in self.active_subjects:
            text += f"📘 *Очередь на {subj}:*\n"
            queue = self.queues.get(subj, [])
            if queue:
                text += "\n".join([f"{i+1}. {name}" for i, name in enumerate(queue)]) + "\n\n"
            else:
                text += "— пока никого нет —\n\n"
        return text.strip()
