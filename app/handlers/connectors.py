import os
from dotenv import load_dotenv
import requests
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


def get_forecast(location_key: str):
    """
    Получает прогноз погоды для указанного location key на 5 дней.

    Параметры:
    - location_key: Идентификатор местоположения для прогноза.
    """
    
    url = f"https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
    params = {
        "apikey": API_KEY,
        "details": "true"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json().get("DailyForecasts", [])
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
        
        
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9 if fahrenheit is not None else None


def parse_weather_forecast(weather_data, days=5):
    """
    Извлекает главную информацию о погоде из данных и возвращает DataFrame
    с количеством дней от 1 до 5.

    Параметры:
    - weather_data: Данные прогноза погоды в формате JSON.
    - days: Количество дней прогноза, от 1 до 5.
    """
    
    if not (1 <= days <= 5):
        raise ValueError("Параметр days должен быть в диапазоне от 1 до 5.")
    
    
    if "DailyForecasts" not in weather_data:
        raise KeyError("Ключ 'DailyForecasts' отсутствует в данных о погоде.")

    daily_weather_summary = []


    for day in weather_data:
        # Конвертируем значения температуры и скорости ветра
        temperature_max_celsius = fahrenheit_to_celsius(day.get("Temperature", {}).get("Maximum", {}).get("Value"))
        realfeel_max_celsius = fahrenheit_to_celsius(day.get("RealFeelTemperature", {}).get("Maximum", {}).get("Value"))
        wind_speed_kph = day.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value") * 1.60934 if day.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value") else None

        day_summary = {
            "Date": day.get("Date"),
            "Temperature (°C)": temperature_max_celsius,
            "Apparent Temperature (°C)": realfeel_max_celsius,
            "Dew Point (°C)": fahrenheit_to_celsius(day.get("DewPoint", {}).get("Value")),
            "Wind Speed (km/h)": wind_speed_kph,
            "Wind Direction": day.get("Day", {}).get("Wind", {}).get("Direction", {}).get("Localized"),
            "Humidity (%)": day.get("Day", {}).get("RelativeHumidity", {}).get("Average"),
            "Precipitation Probability (%)": day.get("Day", {}).get("PrecipitationProbability"),
            "Cloud Cover (%)": day.get("Day", {}).get("CloudCover"),
            "Visibility (km)": day.get("Day", {}).get("Visibility", {}).get("Metric", {}).get("Value"),
            "Pressure (mb)": day.get("Pressure", {}).get("Metric", {}).get("Value"),
            "UV Index": day.get("AirAndPollen", [{}])[5].get("Value") if len(day.get("AirAndPollen", [])) > 5 else None,
            "Weather Description": day.get("Day", {}).get("IconPhrase"),
        }

        daily_weather_summary.append(day_summary)
        
    
        
    df = pd.DataFrame(daily_weather_summary)
    
    
    print(df)
    
    return df.head(days)


