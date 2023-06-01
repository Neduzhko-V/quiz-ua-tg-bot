import json
import random
from aiogram import Bot, Dispatcher, types, executor

with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

TOKEN = '6039938046:AAGYBvWteseUS05K4p8aVIAxQML5ASjQ5NE'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_scores = {}
used_questions = {}


@dp.message_handler(commands=['start'])
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = 0
    used_questions[user_id] = []

    await message.reply("Привіт👋\nЯ вікторина про Україну 🫶🇺🇦 \nСподіваюся ти набереш високий бал, удачі")
    await ask_question(message.chat.id)


async def ask_question(chat_id):
    user_id = chat_id
    if len(used_questions[user_id]) == len(questions):
        used_questions[user_id] = []  # Якщо всі питання використані, очищає список використаних питань

    available_questions = [q for q in questions if q not in used_questions[user_id]]
    random_question = random.choice(available_questions)
    used_questions[user_id].append(random_question)  # Додать вибране питання до списку використаних питань
    question_text = random_question['question']
    answers = random_question['answers']

    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    random.shuffle(answers)
    for answer in answers:
        keyboard_markup.add(answer)
        
    await bot.send_message(chat_id, question_text, reply_markup=keyboard_markup)


@dp.message_handler()
async def process_answer(message: types.Message):
    user_id = message.from_user.id
    answer = message.text

    for question in questions:
        if answer in question['answers']:
            if answer == question['correct_answer']:
                user_scores[user_id] += question['points']
                await bot.send_message(message.chat.id, "🟢✔️Правильна відповідь!")
            else:
                await bot.send_message(message.chat.id, f"🔴✖️Неправильна відповідь.\nПравильна відповідь: {question['correct_answer']}")
            await check_game_over(message.chat.id)
            return

    await bot.send_message(message.chat.id, "Виникла помилка.")


async def check_game_over(chat_id):
    user_id = chat_id
    if len(used_questions[user_id]) == len(questions):
        score = user_scores[user_id]
        keyboard_markup = types.ReplyKeyboardRemove()
        await bot.send_message(chat_id, f"Гра завершена! Ваш рахунок: {score}/250 балів.\nДля того, щоб почати спочатку, натисніть /start", reply_markup=keyboard_markup)
        used_questions[user_id] = []  # Очистить список використаних питань для нової гри
    else:
        await ask_question(chat_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
