import os
import time
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import threading

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

df = pd.DataFrame()

# Функция для мониторинга директории
def monitor_directory(path="app/data", interval=10):
    global df
    while True:
        try:
            files = [f for f in os.listdir(path) if f.endswith('.csv')]
            if files:
                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(path, x)))
                new_df = pd.read_csv(os.path.join(path, latest_file))
                if not new_df.equals(df):  # Проверка, изменился ли датафрейм
                    df = new_df
                    print(f"Loaded data from {latest_file}")
        except Exception as e:
            print(f"Error loading data: {e}")
        time.sleep(interval)

# Запуск мониторинга директории в отдельном потоке
monitor_thread = threading.Thread(target=monitor_directory)
monitor_thread.daemon = True
monitor_thread.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Weather Forecast Dashboard"),
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": city, "value": city} for city in df["City"].unique()] if not df.empty else [],
        value="Moscow" if not df.empty else None,
        clearable=False
    ),
    dcc.Graph(id="temp-graph"),
    dcc.Graph(id="humidity-graph"),
    dcc.Graph(id="wind-speed-graph"),
    dcc.Interval(
        id="interval-component",
        interval=10 * 1000, 
        n_intervals=0 
    )
])

@app.callback(
    [Output("temp-graph", "figure"),
     Output("humidity-graph", "figure"),
     Output("wind-speed-graph", "figure"),
     Output("city-dropdown", "options"),
     Output("city-dropdown", "value")],
    [Input("city-dropdown", "value"),
     Input("interval-component", "n_intervals")]
)
def update_graphs(selected_city, n_intervals):
    if df.empty:
        return {}, {}, {}, [], None

    city_options = [{"label": city, "value": city} for city in df["City"].unique()]
    if selected_city not in df["City"].unique():
        selected_city = city_options[0]["value"]  # Выбираем первый город, если выбранный город отсутствует

    return (
        generate_temp_figure(df, selected_city),
        generate_humidity_figure(df, selected_city),
        generate_wind_speed_figure(df, selected_city),
        city_options,
        selected_city
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
