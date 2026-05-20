from aiogram import Router, F, types
from services.for_handlers import for_analytics
from db import Repo

router = Router()


@router.message(lambda message: message.text == "моя аналитика")
@router.callback_query(F.data == "моя аналитика")
async def show_analytics(event: types.CallbackQuery | types.Message, repo: Repo) -> None:
    """Показывает аналитику пользователя"""
    user_id = event.from_user.id
    
    if isinstance(event, types.CallbackQuery):
        await event.message.answer(await for_analytics.get_analytics_message(user_id, repo), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(await for_analytics.get_analytics_message(user_id, repo), parse_mode="Markdown")
