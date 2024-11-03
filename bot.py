from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'recommend': 'Порекомендовать книгу или фильм по описанию'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })


# Задание 1
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == 'gpt' or dialog.mode == 'talk':
        await gpt_dialog(update, context)
    elif dialog.mode == 'quiz':
        await gpt_quiz(update, context)
    else:
        await send_text(update, context, update.message.text)


# Задание 2
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('random')
    message = load_message('random')

    await send_image(update, context, 'random')
    message = await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)


# Задание 3
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'gpt'
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)


# Задание 4
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    message = load_message('talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн - Солист группы Nirvana 🎸',
        'talk_queen': 'Елизавета II - Королева Соединённого Королевства 👑',
        'talk_tolkien': 'Джон Толкиен - Автор книги "Властелин Колец" 📖',
        'talk_nietzsche': 'Фридрих Ницше - Философ 🧠',
        'talk_hawking': 'Стивен Хокинг - Физик 🔬'
    })


async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    person = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(person)
    chat_gpt.set_prompt(prompt)
    greeting = await chat_gpt.add_message('Представься, пожалуйста')
    await send_image(update, context, person)
    await send_text(update, context, greeting)


# Задание 5
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'quiz'
    message = load_message('quiz')
    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на Python',
        'quiz_math': 'Математические теории',
        'quiz_biology': 'Биология'
    })


async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.callback_query.data
    await update.callback_query.answer()
    question = await chat_gpt.add_message(topic)
    await send_text(update, context, question)


async def gpt_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    if answer == 'Правильно!':
        dialog.count += 1
    await send_text_buttons(update, context, f"Количество правильных ответов: {dialog.count}. Следующий вопрос?", {
        'quiz_more': 'Да',
        'quiz_end': 'Закончить',
    })


async def quiz_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    question = await chat_gpt.add_message('quiz_more')
    await send_text(update, context, question)


# Задание 6
async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    message = load_message('recommend')
    prompt = load_prompt('recommend')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'recommend')
    await send_text_buttons(update, context, message, {
        'rec_movie': 'Порекомендовать фильм',
        'rec_book': 'Порекомендовать книгу',
    })


async def rec_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.callback_query.data
    await update.callback_query.answer()
    question = await chat_gpt.add_message(topic)
    await send_text(update, context, question)


dialog = Dialog()
dialog.mode = None
dialog.count = 0
# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(
    "7909709525:AAEM7eZ658URprV2GkhGSOF6SloQZtR3S60").build()

app.add_handler(CommandHandler('start', start))
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('recommend', recommend))
app.add_handler(MessageHandler(filters.TEXT, echo))


# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(talk_button, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz_.*'))
app.add_handler(CallbackQueryHandler(rec_button, pattern='^rec_.*'))
# app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
