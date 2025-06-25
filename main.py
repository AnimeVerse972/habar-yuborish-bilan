from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from keep_alive import keep_alive
import os
import json

load_dotenv()
keep_alive()

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ADMINS = [6486825926, 7575041003]

# === FAYL FUNKSIYALARI ===

def load_codes():
    try:
        with open("anime_posts.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_codes(data):
    with open("anime_posts.json", "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# === YORDAMCHI ===

def is_user_admin(user_id):
    return user_id in ADMINS

async def is_user_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# === FSM HOLATLAR ===

class AdminStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_remove = State()
    waiting_for_admin_id = State()
    waiting_for_broadcast = State()  # Yangi holat qo'shildi

# === /start ===

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    users = load_users()
    if message.from_user.id not in users:
        users.append(message.from_user.id)
        save_users(users)

    if await is_user_subscribed(message.from_user.id):
        buttons = [[KeyboardButton("\ud83d\udce2 Reklama"), KeyboardButton("\ud83d\udcbc Homiylik")]]
        if is_user_admin(message.from_user.id):
            buttons.append([KeyboardButton("\ud83d\udee0 Admin panel")])
        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("\u2705 Obuna bor. Kodni yuboring:", reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Kanal", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")
        ).add(
            InlineKeyboardButton("\u2705 Tekshirish", callback_data="check_sub")
        )
        await message.answer("\u2757 Iltimos, kanalga obuna bo\u2018ling:", reply_markup=markup)

# === XABAR YUBORISH ===

@dp.message_handler(lambda m: m.text == "\ud83d\udd8a Xabar yuborish")
async def start_broadcast(message: types.Message):
    if not is_user_admin(message.from_user.id):
        return await message.answer("\u26d4 Siz admin emassiz!")
    await message.answer("\ud83d\udd8a Yuboriladigan xabar matnini kiriting:")
    await AdminStates.waiting_for_broadcast.set()

@dp.message_handler(state=AdminStates.waiting_for_broadcast)
async def broadcast_message_handler(message: types.Message, state: FSMContext):
    text = message.text
    users = load_users()
    count = 0
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            count += 1
        except Exception as e:
            print(f"Xatolik: {user_id} => {e}")
    await message.answer(f"\u2705 Xabar yuborildi: {count} ta foydalanuvchiga")
    await state.finish()

# === ADMIN PANELGA TUGMA QO'SHAMIZ ===

@dp.message_handler(lambda m: m.text == "\ud83d\udee0 Admin panel")
async def admin_handler(message: types.Message):
    if is_user_admin(message.from_user.id):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            KeyboardButton("\u2795 Kod qo\u2018shish"), KeyboardButton("\ud83d\udcc4 Kodlar ro\u2018yxati")
        )
        markup.add(
            KeyboardButton("\u274c Kodni o\u2018chirish"), KeyboardButton("\ud83d\udcca Statistika")
        )
        markup.add(
            KeyboardButton("\ud83d\udc64 Admin qo\u2018shish"), KeyboardButton("\ud83d\udd8a Xabar yuborish")
        )
        markup.add(KeyboardButton("\ud83d\udd19 Orqaga"))
        await message.answer("\ud83d\udc6e\u200d\u2642\ufe0f Admin paneliga xush kelibsiz!", reply_markup=markup)
    else:
        await message.answer("\u26d4 Siz admin emassiz!")

# === Qolgan funksiya va kodlaringiz pastda qolganicha ishlaydi ===
# === Masalan: kod qo'sish, kodni o'chirish, statistika, kodni yuborish va h.k. ===

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
