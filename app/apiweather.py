import os
import json
from dotenv import load_dotenv
import requests
import pandas as pd


API_KEY = os.getenv("API_KEY")
BASE_URL = "http://dataservice.accuweather.com/currentconditions/v1/"


def get_location_key_by_geoposition(latitude, longitude, api_key):
    """Получаем location_key для широты и долготы."""

    url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={api_key}&q={latitude},{longitude}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            return data["Key"]
        else:
            print("No location found.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_location_key_by_city(city_name, api_key):
    """Получаем location_key для города."""
    
    CITY_SEARCH_URL = "http://dataservice.accuweather.com/locations/v1/cities/search"
    city_url = f"{CITY_SEARCH_URL}?apikey={api_key}&q={city_name}"
    
    response = requests.get(city_url)
    
    if response.status_code == 200:
        city_data = response.json()
        if city_data:
            return city_data[0]["Key"]  # Берем первый результат и получаем ключ
    else:
        print(f"Error: {response.status_code}, {response.text}")
        
    return None





def parse_location_keys(points: list, api_key: str) -> list:
    """
    Парсит список данных, состоящий из пар координат или названий городов, 
    и возвращает список location_keys для каждого элемента.

    Параметры:
    points (list): Список, где каждый элемент может быть либо кортежем (latitude: int, longitude: int),
                 либо строкой с названием города.
    api_key (str): API-ключ для запроса location_key.

    Возвращает:
    list: Список location_keys для каждого элемента.
    """
    
    location_keys = []

    for item in points:
        location_key = None
        if len(item.split('.')) == 2:
            latitude, longitude = list(map(int, item.split('.')))
            location_key = get_location_key_by_geoposition(latitude, longitude, api_key)
        else:
            city = item
            location_key = get_location_key_by_city(city, api_key)
        
        if location_key is None:
            raise ValueError(f"Location key not found for item: {item}")
            
        location_keys.append(location_key)
        
    return location_keys


def get_weather(location_keys: list):
    """
    ### Получает погодные данные для списка местоположений

    Функция принимает список `location_keys`, где каждый элемент — это уникальный ключ местоположения 
    (location_key), соответствующий либо координатам (широта и долгота), либо названию города. 
    На основе каждого `location_key` функция запрашивает и возвращает погодные данные для каждого места.

    #### Параметры:
    - `location_keys` (list): Список location_key, представляющих местоположения для запроса погоды.

    #### Возвращает:
    - `list`: Список погодных данных для каждого местоположения, соответствующего `location_key`.
    """
    
    # TODO: make func


def get_forecast(location_key: str, user_id):
    """
    Получает прогноз погоды для указанного location key на 5 дней и сохраняет его в файл.

    Параметры:
    - location_key: Идентификатор местоположения для прогноза.
    - user_id: Идентификатор пользователя Telegram.
    """
    
    url = f"https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
    params = {
        "apikey": API_KEY,
        "details": "true"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        forecast_data = response.json().get("DailyForecasts", [])
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", f"{user_id}.json")
        with open(file_path, "w") as json_file:
            json.dump(forecast_data, json_file, indent=4)
        
        return forecast_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



        
def fahrenheit_to_celsius(fahrenheit):
    """Переводит температуру из Фаренгейта в Цельсий."""
    if fahrenheit is None:
        return None
    return round((fahrenheit - 32) * 5.0 / 9.0, 1)

def parse_weather_forecast(weather_data, name, days=5):
    """
    Извлекает главную информацию о погоде из данных и возвращает DataFrame
    с количеством дней от 1 до 5.
    """


    daily_weather_summary = []

    for day in weather_data[:days]:
        # Получаем основные температурные и погодные данные
        date = day.get("Date", "").split("T")[0]
        temperature_max_celsius = fahrenheit_to_celsius(day.get("Temperature", {}).get("Maximum", {}).get("Value"))
        realfeel_max_celsius = fahrenheit_to_celsius(day.get("RealFeelTemperature", {}).get("Maximum", {}).get("Value"))
        wind_speed_mph = day.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value")
        wind_speed_kph = round(wind_speed_mph * 1.60934, 2) if wind_speed_mph else None
        wind_direction = day.get("Day", {}).get("Wind", {}).get("Direction", {}).get("Localized")
        
        # Формируем итоговую информацию для дня
        day_summary = {
            "City": name,
            "Date": date,
            "Temperature (°C)": temperature_max_celsius,
            "Apparent Temperature (°C)": realfeel_max_celsius,
            "Wind Speed (km/h)": wind_speed_kph,
            "Wind Direction": wind_direction,
            "Humidity (%)": day.get("Day", {}).get("RelativeHumidity", {}).get("Average"),
            "Precipitation Probability (%)": day.get("Day", {}).get("PrecipitationProbability"),
            "Cloud Cover (%)": day.get("Day", {}).get("CloudCover"),
            "Weather Description": day.get("Day", {}).get("IconPhrase"),
        }
        
        daily_weather_summary.append(day_summary)
        
    # Создаем DataFrame из собранных данных
    df = pd.DataFrame(daily_weather_summary)
    print(df)
    return df



def format_weather_response(df):
    """
    Форматирует информацию о погоде из DataFrame в читаемый текстовый формат.
    """
    response_lines = []

    # Обходим строки DataFrame
    current_city = None
    for index, row in df.iterrows():
        # Если город изменился, добавляем его в ответ
        if current_city != row["City"]:
            current_city = row["City"]
            response_lines.append(f"Город: {current_city}")

        # Добавляем информацию о дне
        response_lines.append(f"День: {row['Date'].replace('-', '_')}")
        response_lines.append(f"  Температура (°C): {row['Temperature (°C)']}")
        response_lines.append(f"  Ощущаемая температура (°C): {row['Apparent Temperature (°C)']}")
        response_lines.append(f"  Скорость ветра (км/ч): {row['Wind Speed (km/h)']}")
        response_lines.append(f"  Направление ветра: {row['Wind Direction']}")
        response_lines.append(f"  Влажность (%): {row['Humidity (%)']}")
        response_lines.append(f"  Вероятность осадков (%): {row['Precipitation Probability (%)']}")
        response_lines.append(f"  Облачность (%): {row['Cloud Cover (%)']}")
        response_lines.append(f"  Описание погоды: {row['Weather Description']}")
        response_lines.append("")  # Добавляем пустую строку для разделения дней

    # Объединяем все строки в один текстовый блок
    return "\n".join(response_lines)



