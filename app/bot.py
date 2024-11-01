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
import pandas as pd


load_dotenv()
BOT_KEY = os.getenv("BOT_KEY")
API_KEY = os.getenv("API_KEY")


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
    points = message.text.split(',')
    await state.update_data(points=points)
    await message.answer("Please enter the number of days for the weather forecast (from 1 to 5).")
    await state.set_state(RouteForm.days)


# Получение количества дней прогноза
@dp.message(RouteForm.days)
async def process_days(message: types.Message, state: FSMContext):
    try:
        # Отладочное сообщение, чтобы увидеть, что вводит пользователь
        logging.info(f"User input for days: {message.text}")
        days = int(message.text)
        if not (1 <= days <= 5):
            await message.answer("Please enter a valid number of days (from 1 to 5).")
            return
        user_data = await state.get_data()
        points = user_data.get('points', [])
        if not points:
            await message.answer("No route points found. Please start over.")
            return

        location_keys = [get_location_key_by_geoposition(*list(map(int, point.split('.'))), API_KEY) if '.' in point
                        else get_location_key_by_city(point, API_KEY) 
                        for point in points]


        global forecasts #TODO: 😨
        
        
        forecasts = []

        user_id = message.from_user.id

        for name, place in zip(points, location_keys):
            weather_data = get_forecast(place, user_id)
            forecasts.append(parse_weather_forecast(weather_data, name, days))

        response = f"**Route:**\n"
        response += f"**Points:** {', '.join(points)}\n"
        response += f"**Forecast days:** {days} days\n\n"

        await message.answer(response)

        for pred in forecasts:
            response = format_weather_response(pred)
            await message.answer(response)
            
        
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
    

