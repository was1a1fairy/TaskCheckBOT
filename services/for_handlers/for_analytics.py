import numpy as np
from db import Repo


async def get_analytics_message(user_id: int, db: Repo) -> str:
    """Формирует сообщение с аналитикой пользователя"""
    analytics = await db.get_user_analytics(user_id)
    
    total = analytics["total_tasks"]
    completed = analytics["completed_tasks"]
    priority_stats = analytics["priority_stats"]
    
    if total == 0:
        return "У вас пока нет задач для аналитики. Добавьте первую задачу!"
    
    # Процент выполнения
    completion_rate = (completed / total) * 100
    
    # Статистика по приоритетам
    high = priority_stats.get("high", 0)
    medium = priority_stats.get("medium", 0)
    low = priority_stats.get("low", 0)
    
    # Процентное распределение по приоритетам
    priority_dist = {}
    if total > 0:
        priority_dist["high"] = (high / total) * 100
        priority_dist["medium"] = (medium / total) * 100
        priority_dist["low"] = (low / total) * 100
    
    message = (
        f"📊 *Ваша аналитика*\n\n"
        f"Всего задач: {total}\n"
        f"Выполнено: {completed} ({completion_rate:.1f}%)\n"
        f"Осталось: {total - completed}\n\n"
        f"📈 *Распределение по приоритетам:*\n"
        f"🔴 Высокий: {high} ({priority_dist.get('high', 0):.1f}%)\n"
        f"🟡 Средний: {medium} ({priority_dist.get('medium', 0):.1f}%)\n"
        f"🟢 Низкий: {low} ({priority_dist.get('low', 0):.1f}%)"
    )
    
    return message
