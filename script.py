import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

API_KEY = '2943bddce0a694355a7b628410e05198'
CITY = input("Enter city name: ")
UNITS = 'metric'

def get_current_weather(api_key, city, units='metric'):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': units
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return response, data

def display_current_weather(response, data):
    if response.status_code == 200 and data.get("cod") != "404":
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]

        temperature = main.get("temp", "N/A")
        pressure = main.get("pressure", "N/A")
        humidity = main.get("humidity", "N/A")
        description = weather.get("description", "N/A")

        print(f"\nWeather in {CITY}:")
        print(f"Temperature: {temperature}°C")
        print(f"Pressure: {pressure} hPa")
        print(f"Humidity: {humidity}%")
        print(f"Description: {description.capitalize()}")
    else:
        print("\nCity not found or invalid API key.")

def get_forecast(api_key, city, units='metric'):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': api_key,
        'units': units
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return response, data

def process_forecast_data(forecast_data):
    forecast_list = []
    for item in forecast_data['list']:
        forecast = {
            'datetime': datetime.fromtimestamp(item['dt']),
            'date': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d'),
            'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
            'temp': item['main']['temp'],
            'feels_like': item['main']['feels_like'],
            'temp_min': item['main']['temp_min'],
            'temp_max': item['main']['temp_max'],
            'humidity': item['main']['humidity'],
            'pressure': item['main']['pressure'],
            'weather': item['weather'][0]['main'],
            'weather_desc': item['weather'][0]['description'],
            'clouds': item['clouds']['all'],
            'wind_speed': item['wind']['speed'],
            'wind_deg': item['wind']['deg']
        }
        forecast_list.append(forecast)
    return pd.DataFrame(forecast_list)

def create_visualizations(current_data, forecast_df):
    sns.set_style("whitegrid")
    plt.figure(figsize=(15, 10))
    plt.suptitle(f"Weather Dashboard for {CITY}", fontsize=16, y=1.02)
    plt.subplot(2, 2, 1)
    current_temp = current_data['main']['temp']
    weather_desc = current_data['weather'][0]['description'].title()
    plt.text(0.5, 0.7, f"{current_temp}°C", fontsize=48, ha='center')
    plt.text(0.5, 0.5, weather_desc, fontsize=16, ha='center')
    plt.text(0.5, 0.3, f"Humidity: {current_data['main']['humidity']}%", fontsize=12, ha='center')
    plt.text(0.5, 0.2, f"Wind: {current_data['wind']['speed']} m/s", fontsize=12, ha='center')
    plt.axis('off')
    plt.title('Current Weather', pad=20)
    
    plt.subplot(2, 2, 2)
    daily_avg = forecast_df.groupby('date').agg({'temp': 'mean'}).reset_index()
    sns.lineplot(data=daily_avg, x='date', y='temp', marker='o')
    plt.title('5-Day Temperature Forecast')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 3)
    sns.lineplot(data=forecast_df, x='datetime', y='humidity')
    plt.title('Humidity Forecast')
    plt.xlabel('Time')
    plt.ylabel('Humidity (%)')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 4)
    weather_counts = forecast_df['weather'].value_counts()
    plt.pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Weather Conditions Distribution')
    
    plt.tight_layout()
    plt.savefig('weather_dashboard.png', bbox_inches='tight', dpi=300)
    plt.show()

def main():
    response, current_weather = get_current_weather(API_KEY, CITY, UNITS)
    display_current_weather(response, current_weather)
    
    forecast_response, forecast_data = get_forecast(API_KEY, CITY, UNITS)
    
    if forecast_response.status_code == 200 and forecast_data.get("cod") != "404":
        forecast_df = process_forecast_data(forecast_data)
        create_visualizations(current_weather, forecast_df)
        forecast_df.to_csv('weather_forecast.csv', index=False)
        print("\nData saved to weather_forecast.csv")
        print("Dashboard saved to weather_dashboard.png")
    else:
        print("\nFailed to fetch forecast data")

if __name__ == "__main__":
    main()
