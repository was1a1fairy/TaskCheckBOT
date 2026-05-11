from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from typing import Callable,Dict,Any,Awaitable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db import Repo


class Register(BaseMiddleware):

    def __init__(self):
        self.users = []

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        message = event.message

        if not message or not message.from_user:
            return await handler(event, data)

        repo: Repo = data.get("repo")

        user_id = message.from_user.id

        if message.text == "продолжить без регистрации":
            self.users.append(user_id)
            return await handler(event, data)

        if message.text == "зарегистрироваться" or message.text == "войти" or :
            # как мне проверить state.......................
            return await handler(event, data)

        user_exists = await repo.search_user(user_id)

        if user_id in self.users or user_exists:
            return await handler(event, data)
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
            await message.answer(
                text="Зарегистрируйтесь, чтобы пользоваться ботом с разных аккаунтов...",
                reply_markup=reply_markup
            )
            return
