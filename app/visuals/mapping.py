import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Обновлённые данные для нескольких городов
weather_data = [
    {"City": "Moscow", "Date": "2024-11-01", "Temperature (°C)": 12, "Apparent Temperature (°C)": 10, "Humidity (%)": 85, "Wind Speed (km/h)": 15, "Weather Description": "Overcast"},
    {"City": "Moscow", "Date": "2024-11-02", "Temperature (°C)": 14, "Apparent Temperature (°C)": 12, "Humidity (%)": 80, "Wind Speed (km/h)": 10, "Weather Description": "Partly cloudy"},
    {"City": "Moscow", "Date": "2024-11-03", "Temperature (°C)": 10, "Apparent Temperature (°C)": 8, "Humidity (%)": 78, "Wind Speed (km/h)": 20, "Weather Description": "Rainy"},
    {"City": "Moscow", "Date": "2024-11-04", "Temperature (°C)": 9, "Apparent Temperature (°C)": 7, "Humidity (%)": 82, "Wind Speed (km/h)": 18, "Weather Description": "Cloudy"},
    {"City": "Moscow", "Date": "2024-11-05", "Temperature (°C)": 11, "Apparent Temperature (°C)": 9, "Humidity (%)": 76, "Wind Speed (km/h)": 12, "Weather Description": "Clear"},
    
    {"City": "Saint Petersburg", "Date": "2024-11-01", "Temperature (°C)": 8, "Apparent Temperature (°C)": 6, "Humidity (%)": 90, "Wind Speed (km/h)": 14, "Weather Description": "Foggy"},
    {"City": "Saint Petersburg", "Date": "2024-11-02", "Temperature (°C)": 7, "Apparent Temperature (°C)": 5, "Humidity (%)": 85, "Wind Speed (km/h)": 12, "Weather Description": "Overcast"},
    {"City": "Saint Petersburg", "Date": "2024-11-03", "Temperature (°C)": 6, "Apparent Temperature (°C)": 4, "Humidity (%)": 88, "Wind Speed (km/h)": 18, "Weather Description": "Rainy"},
    {"City": "Saint Petersburg", "Date": "2024-11-04", "Temperature (°C)": 10, "Apparent Temperature (°C)": 8, "Humidity (%)": 80, "Wind Speed (km/h)": 16, "Weather Description": "Cloudy"},
    {"City": "Saint Petersburg", "Date": "2024-11-05", "Temperature (°C)": 12, "Apparent Temperature (°C)": 10, "Humidity (%)": 75, "Wind Speed (km/h)": 10, "Weather Description": "Clear"}
]

# Преобразуем данные в DataFrame
df = pd.DataFrame(weather_data)

def generate_temp_figure(df, city):
    city_data = df[df["City"] == city]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=city_data["Date"], y=city_data["Temperature (°C)"],
                             mode="lines+markers", name="Temperature (°C)"))
    fig.add_trace(go.Scatter(x=city_data["Date"], y=city_data["Apparent Temperature (°C)"],
                             mode="lines+markers", name="Feels Like (°C)"))
    fig.update_layout(title=f"Temperature Forecast for {city}", xaxis_title="Date", yaxis_title="Temperature (°C)")
    return fig

def generate_humidity_figure(df, city):
    city_data = df[df["City"] == city]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=city_data["Date"], y=city_data["Humidity (%)"], name="Humidity (%)"))
    fig.update_layout(title=f"Humidity Forecast for {city}", xaxis_title="Date", yaxis_title="Humidity (%)")
    return fig

def generate_wind_speed_figure(df, city):
    city_data = df[df["City"] == city]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=city_data["Date"], y=city_data["Wind Speed (km/h)"],
                             mode="lines+markers", name="Wind Speed (km/h)"))
    fig.update_layout(title=f"Wind Speed Forecast for {city}", xaxis_title="Date", yaxis_title="Wind Speed (km/h)")
    return fig

# Функция запуска сервера Dash на порту 8080

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Weather Forecast Dashboard"),
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": city, "value": city} for city in df["City"].unique()],
        value="Moscow",
        clearable=False
    ),
    dcc.Graph(id="temp-graph"),
    dcc.Graph(id="humidity-graph"),
    dcc.Graph(id="wind-speed-graph")
])

@app.callback(
    [Output("temp-graph", "figure"),
    Output("humidity-graph", "figure"),
    Output("wind-speed-graph", "figure")],
    Input("city-dropdown", "value")
)
def update_graphs(selected_city):
    return (
        generate_temp_figure(df, selected_city),
        generate_humidity_figure(df, selected_city),
        generate_wind_speed_figure(df, selected_city)
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)



