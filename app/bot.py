import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers.connectors import *


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
    # Сохраняем точки маршрута
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
        points = user_data['points']

        print(points, '1')
        # Проверяем, есть ли у нас точки
        if not points:
            await message.answer("No route points found. Please start over.")
            return

        location_keys = parse_location_keys(points, API_KEY)
        print(location_keys, '2')
        
        
        forecasts = []

        for place in location_keys:
            weather_data = get_forecast(place, days)  # Получаем прогноз на 5 дней, затем обрезаем
            print(weather_data[0])
            forecasts.append(parse_weather_forecast(weather_data, days))

        print(forecasts, '4')

        # Формируем ответ с прогнозами погоды
        response = f"**Route:**\n"
        response += f"**Points:** {', '.join(points)}\n"
        response += f"**Forecast days:** {days} days\n\n"

        for idx, forecast in enumerate(forecasts):
            response += f"**Weather Forecast for Location:** {points[idx]}\n"
            for _, day in forecast.iterrows():
                date = day['Date']
                temp = day['Temperature (°C)']
                apparent_temp = day['Apparent Temperature (°C)']
                humidity = day['Humidity (%)']
                wind_speed = day['Wind Speed (km/h)']
                description = day['Weather Description']
                
                response += (f"*Date:* {date}\n"
                            f"*Temperature:* {temp}°C\n"
                            f"*Apparent Temperature:* {apparent_temp}°C\n"
                            f"*Humidity:* {humidity}%\n"
                            f"*Wind Speed:* {wind_speed} km/h\n"
                            f"*Description:* {description}\n\n")

        await message.answer(response, parse_mode='MarkdownV2')


    finally:
        await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
