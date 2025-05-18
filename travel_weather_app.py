"""
Multi-Agent Travel Application
This application uses Strands Agents SDK to find the best weather in California 
for Memorial Day weekend using OpenWeather API.
"""

import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools import calculator, current_time, python_repl

# Load environment variables
load_dotenv()

# Get OpenWeather API key from environment
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise ValueError("OpenWeather API key not found. Please add it to your .env file.")

# List of major cities in California
CALIFORNIA_CITIES = [
    "Los Angeles", "San Francisco", "San Diego", "Sacramento", 
    "San Jose", "Fresno", "Long Beach", "Oakland", "Bakersfield",
    "Anaheim", "Santa Ana", "Riverside", "Stockton", "Irvine",
    "Chula Vista", "Fremont", "Santa Clarita", "San Bernardino",
    "Modesto", "Fontana", "Oxnard", "Moreno Valley", "Santa Rosa",
    "Napa", "Palm Springs", "Santa Barbara", "Monterey", "Laguna Beach",
    "South Lake Tahoe", "Yosemite Valley"
]

# Memorial Day 2025 weekend dates (May 24-26, 2025)
MEMORIAL_DAY_WEEKEND = {
    "start_date": "2025-05-24",
    "end_date": "2025-05-26"
}

@tool
def get_current_weather(city: str) -> dict:
    """
    Get current weather information for a specified city using OpenWeather API.
    
    Args:
        city (str): The name of the city to check weather for
        
    Returns:
        dict: Weather information including temperature, conditions, and humidity
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},CA,US&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {
                "error": f"API request failed with status code {response.status_code}: {response.text}"
            }
            
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "city": city,
            "temperature": f"{data['main']['temp']}°C",
            "feels_like": f"{data['main']['feels_like']}°C",
            "conditions": data['weather'][0]['description'],
            "humidity": f"{data['main']['humidity']}%",
            "wind": f"{data['wind']['speed']} m/s",
            "pressure": f"{data['main']['pressure']} hPa"
        }
        
        return weather_info
    except Exception as e:
        return {"error": str(e)}

@tool
def get_forecast_weather(city: str) -> dict:
    """
    Get 5-day weather forecast for a specified city using OpenWeather API.
    
    Args:
        city (str): The name of the city to check forecast for
        
    Returns:
        dict: Weather forecast information for the next 5 days
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},CA,US&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {
                "error": f"API request failed with status code {response.status_code}: {response.text}"
            }
            
        data = response.json()
        
        # Extract relevant forecast information for Memorial Day weekend
        # Since we can't get exact dates for 2025 from the API now, we'll use the 5-day forecast
        # as a representative sample of the city's weather patterns
        
        daily_forecasts = {}
        for item in data['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'temperatures': [],
                    'conditions': [],
                    'humidity': [],
                    'wind': []
                }
            
            daily_forecasts[date]['temperatures'].append(item['main']['temp'])
            daily_forecasts[date]['conditions'].append(item['weather'][0]['description'])
            daily_forecasts[date]['humidity'].append(item['main']['humidity'])
            daily_forecasts[date]['wind'].append(item['wind']['speed'])
        
        # Calculate averages for each day
        forecast_summary = []
        for date, values in daily_forecasts.items():
            avg_temp = sum(values['temperatures']) / len(values['temperatures'])
            most_common_condition = max(set(values['conditions']), key=values['conditions'].count)
            avg_humidity = sum(values['humidity']) / len(values['humidity'])
            avg_wind = sum(values['wind']) / len(values['wind'])
            
            forecast_summary.append({
                'date': date,
                'avg_temperature': f"{avg_temp:.1f}°C",
                'condition': most_common_condition,
                'avg_humidity': f"{avg_humidity:.1f}%",
                'avg_wind': f"{avg_wind:.1f} m/s"
            })
        
        return {
            "city": city,
            "forecast": forecast_summary
        }
    except Exception as e:
        return {"error": str(e)}

@tool
def get_california_cities() -> list:
    """
    Get a list of major cities in California.
    
    Returns:
        list: Names of major California cities
    """
    return CALIFORNIA_CITIES

@tool
def get_memorial_day_info() -> dict:
    """
    Get information about Memorial Day weekend dates.
    
    Returns:
        dict: Start and end dates for Memorial Day weekend
    """
    return MEMORIAL_DAY_WEEKEND

# Create the Weather Research Agent
weather_researcher = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    tools=[get_current_weather, get_forecast_weather, get_california_cities, calculator],
    system_prompt="""You are a Weather Research Assistant. 
    Your job is to analyze weather data for different cities in California.
    Provide detailed information about current conditions and forecasts.
    When analyzing weather, consider temperature, precipitation, humidity, and wind.
    """
)

# Create the Travel Recommendation Agent
travel_advisor = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    tools=[get_memorial_day_info, python_repl, calculator],
    system_prompt="""You are a Travel Advisor specializing in California destinations.
    Your job is to recommend the best cities to visit based on weather conditions.
    Consider factors like temperature (20-25°C is ideal), clear skies, low precipitation chance,
    and moderate humidity (40-60%).
    Provide detailed recommendations with reasoning.
    """
)

# Create the Coordinator Agent
coordinator = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    tools=[current_time],
    system_prompt="""You are a Travel Planning Coordinator.
    Your job is to coordinate between the Weather Research Assistant and Travel Advisor
    to find the best city in California to visit during Memorial Day weekend based on weather.
    Summarize findings and make a final recommendation.
    """
)

def run_multi_agent_system():
    """
    Run the multi-agent system to find the best city in California for Memorial Day weekend.
    """
    print("🌞 California Memorial Day Weekend Weather Finder 🌞")
    print("Finding the best weather in California for Memorial Day weekend 2025...")
    
    # Step 1: Get the list of cities and Memorial Day info
    cities_response = weather_researcher("What are the major cities in California that we should check for weather?")
    memorial_day_info = travel_advisor("When exactly is Memorial Day weekend in 2025?")
    
    print("\n--- Cities to Check ---")
    print(cities_response)
    print("\n--- Memorial Day Weekend Info ---")
    print(memorial_day_info)
    
    # Step 2: Get weather forecasts for each city
    weather_data_prompt = """
    Please check the weather forecasts for these California cities:
    - San Francisco
    - Los Angeles
    - San Diego
    - Santa Barbara
    - Monterey
    - Palm Springs
    - South Lake Tahoe
    - Napa
    
    Analyze which cities are likely to have the best weather for Memorial Day weekend (May 24-26, 2025).
    Consider temperature, precipitation chance, and overall conditions.
    """
    
    weather_analysis = weather_researcher(weather_data_prompt)
    
    print("\n--- Weather Analysis ---")
    print(weather_analysis)
    
    # Step 3: Get travel recommendations based on weather
    recommendation_prompt = f"""
    Based on this weather analysis:
    
    {weather_analysis}
    
    Which California city would you recommend for a visit during Memorial Day weekend (May 24-26, 2025)?
    Please explain your reasoning and provide details about why this location offers the best weather experience.
    """
    
    travel_recommendation = travel_advisor(recommendation_prompt)
    
    print("\n--- Travel Recommendation ---")
    print(travel_recommendation)
    
    # Step 4: Final coordination and summary
    final_prompt = f"""
    Please review the weather analysis and travel recommendation:
    
    Weather Analysis:
    {weather_analysis}
    
    Travel Recommendation:
    {travel_recommendation}
    
    Provide a final summary and recommendation for the best city in California to visit during 
    Memorial Day weekend 2025 based on weather conditions. Include any additional considerations 
    travelers should keep in mind.
    """
    
    final_recommendation = coordinator(final_prompt)
    
    print("\n--- Final Recommendation ---")
    print(final_recommendation)
    
    return final_recommendation

if __name__ == "__main__":
    run_multi_agent_system()
