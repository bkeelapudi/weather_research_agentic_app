"""
Multi-Agent Travel Application
This application uses Strands Agents SDK to find the best weather in any US state
for Memorial Day weekend using OpenWeather API.
Uses Amazon Bedrock models for different agents.
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

# Dictionary of major cities by US state
US_CITIES_BY_STATE = {
    "Alabama": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Sedona", "Flagstaff"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro"],
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose", "Fresno", "Long Beach", "Oakland", "Bakersfield", "Anaheim", "Santa Ana", "Riverside", "Stockton", "Irvine", "Chula Vista", "Fremont", "Santa Clarita", "San Bernardino", "Modesto", "Fontana", "Oxnard", "Moreno Valley", "Santa Rosa", "Napa", "Palm Springs", "Santa Barbara", "Monterey", "Laguna Beach", "South Lake Tahoe", "Yosemite Valley"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Boulder", "Aspen", "Vail"],
    "Connecticut": ["Bridgeport", "New Haven", "Hartford", "Stamford", "Waterbury"],
    "Delaware": ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna"],
    "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Key West", "Fort Lauderdale", "Tallahassee", "Naples", "Sarasota"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah"],
    "Hawaii": ["Honolulu", "Hilo", "Kailua", "Kaneohe", "Waipahu", "Lahaina", "Kihei"],
    "Idaho": ["Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello"],
    "Illinois": ["Chicago", "Aurora", "Rockford", "Joliet", "Naperville"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City"],
    "Kansas": ["Wichita", "Overland Park", "Kansas City", "Olathe", "Topeka"],
    "Kentucky": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles"],
    "Maine": ["Portland", "Lewiston", "Bangor", "South Portland", "Auburn"],
    "Maryland": ["Baltimore", "Frederick", "Rockville", "Gaithersburg", "Annapolis"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Lowell", "Cambridge"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Duluth", "Bloomington"],
    "Mississippi": ["Jackson", "Gulfport", "Southaven", "Hattiesburg", "Biloxi"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield", "Columbia", "Independence"],
    "Montana": ["Billings", "Missoula", "Great Falls", "Bozeman", "Helena"],
    "Nebraska": ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney"],
    "Nevada": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks", "Carson City"],
    "New Hampshire": ["Manchester", "Nashua", "Concord", "Derry", "Dover"],
    "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton"],
    "New Mexico": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell"],
    "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Asheville"],
    "North Dakota": ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond"],
    "Oregon": ["Portland", "Salem", "Eugene", "Gresham", "Hillsboro", "Bend"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
    "Rhode Island": ["Providence", "Warwick", "Cranston", "Pawtucket", "East Providence"],
    "South Carolina": ["Columbia", "Charleston", "North Charleston", "Mount Pleasant", "Rock Hill"],
    "South Dakota": ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington", "Corpus Christi", "Plano", "Lubbock"],
    "Utah": ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem", "Park City", "Moab"],
    "Vermont": ["Burlington", "South Burlington", "Rutland", "Essex Junction", "Bennington"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Olympia"],
    "West Virginia": ["Charleston", "Huntington", "Parkersburg", "Morgantown", "Wheeling"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine"],
    "Wyoming": ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs"]
}

# Memorial Day 2025 weekend dates (May 24-26, 2025)
MEMORIAL_DAY_WEEKEND = {
    "start_date": "2025-05-24",
    "end_date": "2025-05-26"
}

@tool
def get_current_weather(city: str, state: str) -> dict:
    """
    Get current weather information for a specified city using OpenWeather API.
    
    Args:
        city (str): The name of the city to check weather for
        state (str): The US state where the city is located
        
    Returns:
        dict: Weather information including temperature, conditions, and humidity
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{state},US&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {
                "error": f"API request failed with status code {response.status_code}: {response.text}"
            }
            
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "city": city,
            "state": state,
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
def get_forecast_weather(city: str, state: str) -> dict:
    """
    Get 5-day weather forecast for a specified city using OpenWeather API.
    
    Args:
        city (str): The name of the city to check forecast for
        state (str): The US state where the city is located
        
    Returns:
        dict: Weather forecast information for the next 5 days
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},{state},US&appid={OPENWEATHER_API_KEY}&units=metric"
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
            "state": state,
            "forecast": forecast_summary
        }
    except Exception as e:
        return {"error": str(e)}

@tool
def get_us_states() -> list:
    """
    Get a list of all US states.
    
    Returns:
        list: Names of all US states
    """
    return list(US_CITIES_BY_STATE.keys())

@tool
def get_cities_by_state(state: str) -> list:
    """
    Get a list of major cities in the specified US state.
    
    Args:
        state (str): The name of the US state
        
    Returns:
        list: Names of major cities in the state
    """
    if state in US_CITIES_BY_STATE:
        return US_CITIES_BY_STATE[state]
    else:
        return []

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

# Create all agents using Amazon Bedrock Claude models
weather_researcher = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",  # Amazon Bedrock Claude model
    tools=[get_current_weather, get_forecast_weather, get_cities_by_state, calculator, analyze_weather_comfort],
    system_prompt="""You are a Weather Research Assistant specialized in US climate patterns. 
    Your job is to analyze weather data for different cities in any US state.
    Provide detailed information about current conditions and forecasts.
    When analyzing weather, consider temperature, precipitation, humidity, and wind.
    Use the analyze_weather_comfort tool to evaluate overall comfort levels.
    """
)

# Create the Travel Recommendation Agent using Amazon Bedrock Claude
travel_advisor = Agent(
    model="anthropic.claude-3-sonnet-20240229-v1:0",  # Amazon Bedrock Claude model
    tools=[get_memorial_day_info, python_repl, calculator, analyze_weather_comfort],
    system_prompt="""You are a Travel Advisor specializing in US destinations.
    Your job is to recommend the best cities to visit based on weather conditions.
    Consider factors like temperature (20-25°C is ideal), clear skies, low precipitation chance,
    and moderate humidity (40-60%).
    Provide detailed recommendations with reasoning.
    Use the analyze_weather_comfort tool to evaluate and compare destinations.
    """
)

# Create the Coordinator Agent using Amazon Bedrock Claude
coordinator = Agent(
    model="anthropic.claude-3-haiku-20240307-v1:0",  # Amazon Bedrock Claude model
    tools=[current_time],
    system_prompt="""You are a Travel Planning Coordinator.
    Your job is to coordinate between the Weather Research Assistant and Travel Advisor
    to find the best city in a US state to visit during Memorial Day weekend based on weather.
    Summarize findings and make a final recommendation.
    Include specific details about expected weather conditions and why they make for an ideal visit.
    """
)

import re

def extract_recommended_city(recommendation_text, cities_list):
    """
    Extract the recommended city from the recommendation text
    
    Args:
        recommendation_text (str or AgentResult): The text of the recommendation
        cities_list (list): List of cities to check for in the recommendation
        
    Returns:
        str: The name of the recommended city
    """
    # Convert AgentResult to string if needed
    if hasattr(recommendation_text, 'content'):
        recommendation_text = recommendation_text.content
    elif not isinstance(recommendation_text, str):
        recommendation_text = str(recommendation_text)
    
    # Check for explicit recommendation statements with stronger indicators
    strong_recommendation_phrases = [
        "final recommendation is", "we recommend", "I recommend", 
        "best city is", "top choice is", "recommend visiting", 
        "ideal destination is", "best destination is"
    ]
    
    # First look for strong explicit recommendations
    for phrase in strong_recommendation_phrases:
        for city in cities_list:
            pattern = f"{phrase}.*{city}"
            if re.search(pattern, recommendation_text, re.IGNORECASE):
                return city
    
    # Then check for cities mentioned with positive sentiment
    positive_phrases = [
        "excellent weather", "ideal conditions", "perfect weather",
        "best weather", "highest comfort score", "most comfortable"
    ]
    
    for phrase in positive_phrases:
        for city in cities_list:
            if f"{city}.*{phrase}" in recommendation_text or f"{phrase}.*{city}" in recommendation_text:
                return city
    
    # Check for cities mentioned at the beginning of sentences (likely more important)
    for city in cities_list:
        pattern = f"[.!?]\s+{city}"
        if re.search(pattern, recommendation_text) or recommendation_text.startswith(city):
            return city
    
    # If no strong recommendation found, check for any mention of cities
    for city in cities_list:
        if city in recommendation_text:
            return city
    
    # Default to the first city in our list if no clear recommendation
    if cities_list:
        return cities_list[0]
    else:
        return "No recommendation available"

def run_multi_agent_system(state):
    """
    Run the multi-agent system to find the best city in the specified state for Memorial Day weekend.
    
    Args:
        state (str): The US state to analyze
        
    Returns:
        tuple: (final_recommendation, recommended_city)
    """
    print(f"🌞 {state} Memorial Day Weekend Weather Finder 🌞")
    print(f"Finding the best weather in {state} for Memorial Day weekend 2025...")
    print("Using Claude models for multi-agent collaboration")
    
    # Step 1: Get the list of cities and Memorial Day info
    cities_response = weather_researcher(f"What are the major cities in {state} that we should check for weather?")
    memorial_day_info = travel_advisor("When exactly is Memorial Day weekend in 2025?")
    
    print("\n--- Cities to Check (Claude Haiku) ---")
    print(cities_response)
    print("\n--- Memorial Day Weekend Info (Claude Sonnet) ---")
    print(memorial_day_info)
    
    # Get the list of cities in the state
    cities = get_cities_by_state(state)
    
    # Select a subset of cities if there are too many
    if len(cities) > 8:
        selected_cities = cities[:8]  # Take the first 8 cities
    else:
        selected_cities = cities
    
    # Step 2: Get weather forecasts for each city
    weather_data_prompt = f"""
    Please check the weather forecasts for these {state} cities:
    - {", ".join(selected_cities)}
    
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
    
    Which {state} city would you recommend for a visit during Memorial Day weekend (May 24-26, 2025)?
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
    
    Provide a final summary and recommendation for the best city in {state} to visit during 
    Memorial Day weekend 2025 based on weather conditions. Include any additional considerations 
    travelers should keep in mind.
    """
    
    final_recommendation = coordinator(final_prompt)
    
    print("\n--- Final Recommendation (Claude Haiku) ---")
    print(final_recommendation)
    
    # Step 5: Extract the recommended city
    recommended_city = extract_recommended_city(final_recommendation, cities)
    print(f"\n--- Recommended City: {recommended_city} ---")
    
    return final_recommendation, recommended_city

if __name__ == "__main__":
    state = input("Enter a US state to analyze: ")
    run_multi_agent_system(state)
