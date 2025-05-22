"""
Multi-Agent Travel Application
This application uses Strands Agents SDK to find the best weather in California 
for Memorial Day weekend using OpenWeather API.
Uses Claude models for different agents.
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

@tool
def analyze_weather_comfort(temperature: float, humidity: float, wind_speed: float) -> dict:
    """
    Analyze weather comfort based on temperature, humidity, and wind speed.
    
    Args:
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage
        wind_speed (float): Wind speed in m/s
        
    Returns:
        dict: Comfort analysis with score and description
    """
    # Calculate comfort score (0-100)
    # Ideal conditions: 20-25°C, 40-60% humidity, 2-5 m/s wind
    temp_score = 100 - min(abs(temperature - 22.5) * 5, 50)
    humidity_score = 100 - min(abs(humidity - 50) * 1.5, 50)
    wind_score = 100 - min(abs(wind_speed - 3.5) * 10, 50)
    
    overall_score = (temp_score + humidity_score + wind_score) / 3
    
    # Determine comfort level
    if overall_score >= 80:
        comfort = "Excellent"
    elif overall_score >= 60:
        comfort = "Good"
    elif overall_score >= 40:
        comfort = "Moderate"
    else:
        comfort = "Poor"
    
    return {
        "comfort_score": overall_score,
        "comfort_level": comfort,
        "temperature_score": temp_score,
        "humidity_score": humidity_score,
        "wind_score": wind_score,
        "analysis": f"Weather comfort is {comfort} with an overall score of {overall_score:.1f}/100"
    }

# Create all agents using Claude model
weather_researcher = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",  # Claude model
    tools=[get_current_weather, get_forecast_weather, get_california_cities, calculator, analyze_weather_comfort],
    system_prompt="""You are a Weather Research Assistant specialized in California climate patterns. 
    Your job is to analyze weather data for different cities in California.
    Provide detailed information about current conditions and forecasts.
    When analyzing weather, consider temperature, precipitation, humidity, and wind.
    Use the analyze_weather_comfort tool to evaluate overall comfort levels.
    """
)

# Create the Travel Recommendation Agent using Claude Sonnet (more powerful)
travel_advisor = Agent(
    model="anthropic.claude-3-sonnet-20240229-v1:0",  # Claude Sonnet model
    tools=[get_memorial_day_info, python_repl, calculator, analyze_weather_comfort],
    system_prompt="""You are a Travel Advisor specializing in California destinations.
    Your job is to recommend the best cities to visit based on weather conditions.
    Consider factors like temperature (20-25°C is ideal), clear skies, low precipitation chance,
    and moderate humidity (40-60%).
    Provide detailed recommendations with reasoning.
    Use the analyze_weather_comfort tool to evaluate and compare destinations.
    """
)

# Create the Coordinator Agent using Claude model
coordinator = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",  # Claude model
    tools=[current_time],
    system_prompt="""You are a Travel Planning Coordinator.
    Your job is to coordinate between the Weather Research Assistant and Travel Advisor
    to find the best city in California to visit during Memorial Day weekend based on weather.
    Summarize findings and make a final recommendation.
    Include specific details about expected weather conditions and why they make for an ideal visit.
    """
)

import re

def extract_recommended_city(recommendation_text):
    """
    Extract the recommended city from the recommendation text
    
    Args:
        recommendation_text (str or AgentResult): The text of the recommendation
        
    Returns:
        str: The name of the recommended city
    """
    # Convert AgentResult to string if needed
    if hasattr(recommendation_text, 'content'):
        recommendation_text = recommendation_text.content
    elif not isinstance(recommendation_text, str):
        recommendation_text = str(recommendation_text)
    
    # List of cities to check for in the recommendation
    cities_to_check = [
        "Palm Springs", "Santa Barbara", "Los Angeles", "San Diego", 
        "Monterey", "Napa", "San Francisco", "South Lake Tahoe"
    ]
    
    # Check for explicit recommendation statements with stronger indicators
    strong_recommendation_phrases = [
        "final recommendation is", "we recommend", "I recommend", 
        "best city is", "top choice is", "recommend visiting", 
        "ideal destination is", "best destination is"
    ]
    
    # First look for strong explicit recommendations
    for phrase in strong_recommendation_phrases:
        for city in cities_to_check:
            pattern = f"{phrase}.*{city}"
            if re.search(pattern, recommendation_text, re.IGNORECASE):
                return city
    
    # Then check for cities mentioned with positive sentiment
    positive_phrases = [
        "excellent weather", "ideal conditions", "perfect weather",
        "best weather", "highest comfort score", "most comfortable"
    ]
    
    for phrase in positive_phrases:
        for city in cities_to_check:
            if f"{city}.*{phrase}" in recommendation_text or f"{phrase}.*{city}" in recommendation_text:
                return city
    
    # Check for cities mentioned at the beginning of sentences (likely more important)
    for city in cities_to_check:
        pattern = f"[.!?]\s+{city}"
        if re.search(pattern, recommendation_text) or recommendation_text.startswith(city):
            return city
    
    # If no strong recommendation found, check for any mention of cities
    for city in cities_to_check:
        if city in recommendation_text:
            return city
    
    # Default to the first city in our list if no clear recommendation
    return "Palm Springs"  # Default to Palm Springs as it was the most likely recommendation

def run_multi_agent_system():
    """
    Run the multi-agent system to find the best city in California for Memorial Day weekend.
    """
    print("🌞 California Memorial Day Weekend Weather Finder 🌞")
    print("Finding the best weather in California for Memorial Day weekend 2025...")
    print("Using Claude models for multi-agent collaboration")
    
    # Step 1: Get the list of cities and Memorial Day info
    cities_response = weather_researcher("What are the major cities in California that we should check for weather?")
    memorial_day_info = travel_advisor("When exactly is Memorial Day weekend in 2025?")
    
    print("\n--- Cities to Check (Claude Haiku) ---")
    print(cities_response)
    print("\n--- Memorial Day Weekend Info (Claude Sonnet) ---")
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
    Use the analyze_weather_comfort tool to evaluate each city's comfort level.
    """
    
    weather_analysis = weather_researcher(weather_data_prompt)
    
    print("\n--- Weather Analysis (Claude Haiku) ---")
    print(weather_analysis)
    
    # Step 3: Get travel recommendations based on weather
    recommendation_prompt = f"""
    Based on this weather analysis:
    
    {weather_analysis}
    
    Which California city would you recommend for a visit during Memorial Day weekend (May 24-26, 2025)?
    Please explain your reasoning and provide details about why this location offers the best weather experience.
    Use the analyze_weather_comfort tool to evaluate your top recommendations.
    """
    
    travel_recommendation = travel_advisor(recommendation_prompt)
    
    print("\n--- Travel Recommendation (Claude Sonnet) ---")
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
    
    print("\n--- Final Recommendation (Claude Haiku) ---")
    print(final_recommendation)
    
    # Step 5: Extract the recommended city
    recommended_city = extract_recommended_city(final_recommendation)
    print(f"\n--- Recommended City: {recommended_city} ---")
    
    return final_recommendation, recommended_city

if __name__ == "__main__":
    run_multi_agent_system()
