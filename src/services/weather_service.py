import random
import json
from datetime import datetime, timedelta
from model.model_datastore import model
from utils.caching import cache_response
from utils.html_utils import generate_html_page, generate_download_page
from fastapi.responses import JSONResponse, HTMLResponse
from utils.file_utils import save_file

db = model()  # Datastore Model

SEASON_TEMPERATURES = {
    "Winter": (-10, 5),
    "Spring": (5, 20),
    "Summer": (15, 35),
    "Fall": (5, 20)
}

CONDITIONS = {
    "Sunny": "Clear skies and warm temperatures.",
    "Cloudy": "Overcast skies with mild temperatures.",
    "Rainy": "Showers expected throughout the day.",
    "Snowy": "Snowy weather, please bundle up!",
    "Windy": "Breezy with gusts of wind."
}

CSS_STYLES_DATE = {
    ".date": "font-size: 16px; font-weight: bold; color: #000000; margin: 5px 0;",  
    ".temperature": "font-size: 16px; font-weight: bold; color: #8B0000; margin: 5px 0;",  
    ".wind": "font-size: 16px; font-weight: bold; color: #004085; margin: 5px 0;", 
    ".precipitation": "font-size: 16px; font-weight: bold; color: #155724; margin: 5px 0;",  
    
    ".sunny": "color: orange; font-weight: bold; font-size: 16px; margin: 5px 0;",
    ".cloudy": "color: gray; font-weight: bold; font-size: 16px; margin: 5px 0;",
    ".rainy": "color: blue; font-weight: bold; font-size: 16px; margin: 5px 0;",
    ".snowy": "color: lightblue; font-weight: bold; font-size: 16px; margin: 5px 0;",
    ".windy": "color: green; font-weight: bold; font-size: 16px; margin: 5px 0;"
}




CSS_STYLES_MONTH = {
    "table": "width: 100%; border-collapse: collapse;",
    "th, td": "border: 1px solid black; padding: 8px; text-align: center;",
    "th": "background-color: #f2f2f2; font-weight: bold;",
    ".sunny": "background-color: #ffeeba; color: #8a5700; font-weight: bold;", 
    ".cloudy": "background-color: #d6d6d6; color: #333333; font-weight: bold;",  
    ".rainy": "background-color: #cce5ff; color: #004085; font-weight: bold;",  
    ".snowy": "background-color: #e3f2fd; color: #0d47a1; font-weight: bold;",  
    ".windy": "background-color: #d4edda; color: #155724; font-weight: bold;"   
}




def get_season(month: int) -> str:
    """Determine season based on the month."""
    if month in [12, 1, 2]: return "Winter"
    if month in [3, 4, 5]: return "Spring"
    if month in [6, 7, 8]: return "Summer"
    return "Fall"

def generate_weather_data(date: str):
    """Generates randomized weather data."""
    month = int(date.split("-")[1])
    season = get_season(month)

    temp_range = SEASON_TEMPERATURES[season]
    temp = random.randint(temp_range[0], temp_range[1])
    wind = random.randint(5, 30)

    if season == "Winter":
        precipitation = random.randint(0, 20)
    elif season == "Summer":
        precipitation = random.randint(0, 10)
    else:
        precipitation = random.randint(0, 15)

    if precipitation == 0:
        condition = "Sunny"
    elif season == "Winter" and temp <= 0 and precipitation > 8:
        condition = "Snowy"
    elif precipitation > 12:
        condition = "Rainy"
    else:
        condition = random.choice(["Cloudy", "Windy"])

    description = CONDITIONS[condition]

    weather_data = {
        "date": date,
        "temperature": temp,
        "wind": wind,
        "precipitation": precipitation,
        "condition": condition,
        "description": description
    }

    return json.loads(json.dumps(weather_data))

def get_weather_for_date(date: str, format: str = "json"):
    cache_key = f"weather:{date}:{format}"
    cached_data = cache_response.get(cache_key)

    if cached_data:
        if format == "json":
            return JSONResponse(content=cached_data)
        elif format in ["html", "download"]:
            return generate_weather_html_response(cached_data, date, format)

    existing_data = db.get_weather_data(date)

    if existing_data:
        response = existing_data
    else:
        response = generate_weather_data(date)
        db.store_weather_data(date, response)

    cache_response.set(cache_key, response, expire=3600)

    if format == "json":
        return JSONResponse(content=response)
    elif format in ["html", "download"]:
        return generate_weather_html_response(response, date, format)

def get_weather_for_month(month: str, format: str = "json"):
    year, month_number = map(int, month.split("-"))
    days_in_month = (datetime(year, month_number + 1, 1) - timedelta(days=1)).day
    cache_key = f"weather:month:{month}:{format}"

    cached_data = cache_response.get(cache_key)
    if cached_data:
        if format == "json":
            return JSONResponse(content=cached_data)
        elif format in ["html", "download"]:
            return generate_month_html_response(cached_data, month, format)

    existing_days = db.get_weather_days_in_month(month)

    if len(existing_days) != days_in_month:
        db.clear_weather_month(month)
        weather_data = [generate_weather_data(f"{month}-{str(day).zfill(2)}") for day in range(1, days_in_month + 1)]
        for day in weather_data:
            db.store_weather_data(day["date"], day)
    else:
        weather_data = [db.get_weather_data(f"{month}-{str(day).zfill(2)}") for day in range(1, days_in_month + 1)]

    cache_response.set(cache_key, weather_data, expire=3600)

    if format == "json":
        return JSONResponse(content=weather_data)
    elif format in ["html", "download"]:
        return generate_month_html_response(weather_data, month, format)

  

def generate_weather_html_response(data, date, format):
    """Generate HTML or Downloadable HTML for a single date."""
    content = f"""
    <p class="date">Date: {data['date']} </p>
    <p class="temperature">Temperature: {data['temperature']}°C</p>
    <p class="wind">Wind: {data['wind']} km/h</p>
    <p class="precipitation">Precipitation: {data['precipitation']} mm</p>
    <p class="{data['condition'].lower()}">Condition: {data['condition']}</p>
    """
    
    if format == "html":
        return HTMLResponse(content=generate_html_page("Weather Report", content, styles=CSS_STYLES_DATE))
    
    elif format == "download":
        file_path = save_file(content=generate_html_page("Weather Report", content, CSS_STYLES_DATE), 
                              file_extension="html", folder="static/downloads")
        
        return HTMLResponse(content=generate_download_page("Your Weather Report", file_path, "weather_report.html", CSS_STYLES_DATE))




def generate_month_html_response(data, month, format):
    """Generate HTML or Downloadable HTML for a full month."""
    rows = "".join([
        f"<tr><td>{day['date']}</td><td>{day['temperature']}°C</td>"
        f"<td>{day['wind']} km/h</td><td>{day['precipitation']} mm</td>"
        f"<td class='{day['condition'].lower()}'> {day['condition']} </td></tr>"
        for day in data
    ])
    content = f"<table><tr><th>Date</th><th>Temperature</th><th>Wind</th><th>Precipitation</th><th>Condition</th></tr>{rows}</table>"

    if format == "html":
        return HTMLResponse(content=generate_html_page("Monthly Weather Report", content, styles=CSS_STYLES_MONTH))
    
    elif format == "download":
        file_path = save_file(content=generate_html_page("Monthly Weather Report", content, CSS_STYLES_MONTH), 
                              file_extension="html", folder="static/downloads")
        
        return HTMLResponse(content=generate_download_page("Your Monthly Weather Report", file_path, "monthly_weather_report.html", CSS_STYLES_MONTH))

