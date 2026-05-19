from db import Repo


async def check_reminders(bot, repo: Repo) -> None:
    """Проверяет и отправляет напоминания о задачах с истекающим дедлайном"""
    try:
        tasks = await repo.expired_tasks()
        for user_id, task_name in tasks:
            try:
                await bot.send_message(user_id, f"Напоминание: Задача '{task_name}' истекает через 1 день!")
            except Exception as e:
                print(f"Ошибка отправки напоминания: {e}")

        reminders = await repo.get_pending_reminders()
        for user_id, task_name in reminders:
            try:
                await bot.send_message(user_id, f"Напоминание: Задача '{task_name}' требует внимания!")
                await repo.mark_reminders_sent(user_id, task_name)
            except Exception as e:
                print(f"Ошибка отправки напоминания: {e}")
    except Exception as e:
        print(f"Ошибка в check_reminders: {e}")


def start_reminder_service(scheduler, bot, repo: Repo, days: int = 1) -> None:
    """Запускает сервис напоминаний с заданным интервалом"""
    scheduler.add_job(lambda: check_reminders(bot, repo), 'interval', days=days)
    scheduler.start()