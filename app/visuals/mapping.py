import pandas as pd
import plotly.graph_objects as go

def set_points(coordinates, color_points="blue", color_line="red", zoom=10, height=500):
    """
    Отображает связанные точки на карте с помощью Plotly.
    
    Параметры:
    - coordinates: список кортежей [(lat1, lon1), (lat2, lon2), ...] для отображения на карте
    - color_points: цвет точек
    - color_line: цвет линий
    - zoom: начальный масштаб карты
    - height: высота карты
    
    Возвращает:
    - интерактивную карту с точками, представляющими указанные координаты, и линиями, соединяющими их.
    """
    # Преобразуем список координат в DataFrame
    df = pd.DataFrame(coordinates, columns=["Latitude", "Longitude"])
    
    # Создаем фигуру с линией, соединяющей точки
    fig = go.Figure()

    # Добавляем линию между точками
    fig.add_trace(go.Scattermapbox(
        mode="lines+markers",
        lat=df["Latitude"],
        lon=df["Longitude"],
        marker={'size': 8, 'color': color_points},
        line={'width': 2, 'color': color_line}
    ))

    # Настройки отображения карты
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=zoom,
        mapbox_center={"lat": df["Latitude"].mean(), "lon": df["Longitude"].mean()},
        height=height,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    fig.show()
