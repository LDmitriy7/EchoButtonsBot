""" Echo bot with buttons and html-parse-mode.
You can see markup rules in README.md
"""
from aiogram import Bot, Dispatcher, executor, types
import os

BOT_TOKEN = os.getenv('BOT_TOKEN2')
bot = Bot(BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot)


def make_markup(button_rows: list):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button_row in button_rows:
        kb.row(*button_row)
    return kb


def make_inline_kb(button_rows: list):
    kb = types.InlineKeyboardMarkup()
    for button_row in button_rows:
        row = [types.InlineKeyboardButton(btn, callback_data='.') for btn in button_row]
        kb.row(*row)
    return kb


def parse_reply_markup(reply_markup: str, reply_markup_func):
    rows = reply_markup.split('\n')
    button_rows = []
    for row in rows:
        buttons = [btn.strip() for btn in row.split(',')]
        button_rows.append(buttons)
    kb = reply_markup_func(button_rows)
    return kb


def parse_msg_text(text):
    if '$:' not in text:
        return text, None

    # если есть разметка
    if '$$:' in text:
        text, reply_markup = text.split('$$:')
        reply_markup_func = make_inline_kb
    else:
        text, reply_markup = text.split('$:')
        reply_markup_func = make_markup

    reply_markup = reply_markup.strip()
    kb = parse_reply_markup(reply_markup, reply_markup_func)
    return text, kb


@dp.message_handler()
async def echo_text(msg: types.Message):
    text, kb = parse_msg_text(msg.text)
    await msg.answer(text, reply_markup=kb)


@dp.message_handler(content_types='photo')
async def echo_photo(msg: types.Message):
    caption, kb = None, None
    if msg.caption:
        caption, kb = parse_msg_text(msg.caption)
    await msg.answer_photo(msg.photo[-1].file_id, caption, reply_markup=kb)


@dp.message_handler(content_types='document')
async def echo_document(msg: types.Message):
    caption, kb = None, None
    if msg.caption:
        caption, kb = parse_msg_text(msg.caption)
    await msg.answer_document(msg.document.file_id, caption, reply_markup=kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

