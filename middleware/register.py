from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable,Dict,Any,Awaitable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db import Repo


class Register(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str,Any]], Awaitable[Any]],
            event:Message,
            data: Dict[str,Any]
    ) -> Any:
        user_id = event.from_user.id
        if Repo.search_user(user_id):
            return await handler(event,data)
        else:
            keyboard = [
                [KeyboardButton(text="зарегистрироваться"),
                 KeyboardButton(text="войти")],
                [KeyboardButton(text="продолжить без регистрации")]
            ]

            reply_markup = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
            await event.reply(text="Зарегистрируйтесь, чтобы пользоваться ботом с разных аккаунтов. "
                                   "Без регистрации ваши задачи будут доступны только в чате. мяу",
                              reply_markup=reply_markup)