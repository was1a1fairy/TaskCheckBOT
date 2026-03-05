from aiogram import filters, Router, F, types
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery, KeyboardButton
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
import services.basic
import db

router3 = Router()