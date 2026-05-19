from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Update, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import Repo


class Register(BaseMiddleware):
    def __init__(self, repo: Any) -> None:
        self.users = repo

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user_id = None
        message: Message | None = None

        if event.message:
            message = event.message
            if message.from_user:
                user_id = message.from_user.id
        elif event.callback_query:
            if event.callback_query.from_user:
                user_id = event.callback_query.from_user.id
            message = event.callback_query.message

        if not user_id:
            return await handler(event, data)

        state: FSMContext = data.get("state")
        current_state = await state.get_state() if state else None

        user_exists = await self.users.search_user(user_id)
        if user_exists:
            return await handler(event, data)

        if current_state and "StatesREG" in str(current_state):
            return await handler(event, data)

        if current_state and "StatesLOG" in str(current_state):
            return await handler(event, data)

        if current_state and state:
            await state.clear()

        if not message or not message.text:
            return

        allowed_texts = ["зарегистрироваться", "войти", "продолжить без регистрации"]

        if message.text in allowed_texts:
            if message.text == "продолжить без регистрации":
                await self.users.add_unregistered_user(user_id)
                await message.reply("Вы можете пользоваться ботом! Нажмите /start")
            return await handler(event, data)

        keyboard = [
            [KeyboardButton(text="зарегистрироваться"),
             KeyboardButton(text="войти")],
            [KeyboardButton(text="продолжить без регистрации")]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )

        await message.reply(
            text="Зарегистрируйтесь, чтобы пользоваться ботом с разных аккаунтов...",
            reply_markup=reply_markup
        )
        return

