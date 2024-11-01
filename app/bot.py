import asyncio
import os
import logging
import threading
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from apiweather import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
import pandas as pd


load_dotenv()
BOT_KEY = os.getenv("BOT_KEY")
API_KEY = os.getenv("API_KEY")



days_keyboard_builder = InlineKeyboardBuilder()
for i in range(1, 6):
    days_keyboard_builder.button(text=f"{i}", callback_data=f"days_{i}")
    
days_keyboard: InlineKeyboardMarkup = days_keyboard_builder.as_markup()


logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_KEY)
dp = Dispatcher(storage=MemoryStorage())

# Определяем состояния для маршрута
class RouteForm(StatesGroup):
    points = State()
    days = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Hello! I can help you plan routes and get weather updates.\n\n"
        "Commands:\n"
        "/weather - Plan a route and get a weather forecast\n"
        "/help - Get information on how to use this bot"
    )

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message, state: FSMContext):
    await message.answer("Please enter the route points as coordinates or city names (e.g., '50.50,Moscow,40.20').")
    await state.set_state(RouteForm.points)

# Получение координат от пользователя
@dp.message(RouteForm.points)
async def process_points(message: types.Message, state: FSMContext):
    points = message.text.split(",")
    await state.update_data(points=points)
    await message.answer("Please enter the number of days for the weather forecast (from 1 to 5).", reply_markup=days_keyboard)
    await state.set_state(RouteForm.days)


# Получение количества дней прогноза
@dp.callback_query(lambda callback_query: callback_query.data.startswith("days_"))
async def process_days(query: types.CallbackQuery, state: FSMContext):
    try:
        
        
        days = int(query.data[-1])
        if not (1 <= days <= 5):
            await bot.send_message(query.from_user.id, "Please enter a valid number of days (from 1 to 5).")
            return
        user_data = await state.get_data()
        points = user_data.get("points", [])
        if not points:
            await bot.send_message(query.from_user.id, "No route points found. Please start over.")
            return

        location_keys = [get_location_key_by_geoposition(*list(map(int, point.split("."))), API_KEY) if "." in point
                        else get_location_key_by_city(point, API_KEY) 
                        for point in points]


        global forecasts #TODO: 😨
        
        
        forecasts = []

        user_id = query.from_user.id

        for name, place in zip(points, location_keys):
            weather_data = get_forecast(place, user_id)
            forecasts.append(parse_weather_forecast(weather_data, name, days))

        response = f"**Route:**\n"
        response += f"**Points:** {',' .join(points)}\n"
        response += f"**Forecast days:** {days} days\n\n"

        await bot.send_message(query.from_user.id, response)

        for pred in forecasts:
            response = format_weather_response(pred)
            await bot.send_message(query.from_user.id, response)
            
        
        os.makedirs("app/data", exist_ok=True)
        combined_forecast = pd.concat(forecasts, ignore_index=True)

        file_path = f"app\\data\\{user_id}.csv"
        combined_forecast.to_csv(file_path, index=False)





    finally:
        await state.clear()




@dp.message(Command("graph"))
async def send_graph(message: types.Message):
    await message.reply("Сервер с графиком запущен на https://lizard-maximum-hippo.ngrok-free.app/")




async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    

