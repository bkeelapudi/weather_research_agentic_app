# US State Memorial Day Weather Finder

A multi-agent application that finds the best weather in any US state for Memorial Day weekend using the Strands Agents SDK, Amazon Bedrock Claude models, and OpenWeather API.

1. Weather Researcher Agent - Uses Claude 3 Haiku model
   • Specializes in analyzing weather data for different cities
   • Has access to tools like get_current_weather, get_forecast_weather, and analyze_weather_comfort

2. Travel Advisor Agent - Uses Claude 3 Sonnet model
   • Recommends cities based on weather conditions
   • Has access to tools like get_memorial_day_info and analyze_weather_comfort

3. Coordinator Agent - Uses Claude 3 Haiku model
   • Coordinates between the Weather Researcher and Travel Advisor
   • Synthesizes information and makes the final recommendation



## Overview

This application uses a system of three specialized AI agents powered by Amazon Bedrock Claude models to analyze weather data and provide travel recommendations for Memorial Day weekend in any US state. The agents collaborate to determine which city is likely to have the most pleasant weather conditions during the holiday weekend.

## Features

- Retrieves current weather and 5-day forecasts for major cities in any US state
- Analyzes weather comfort based on temperature, humidity, and wind speed
- Provides detailed weather analysis for Memorial Day weekend
- Generates travel recommendations with reasoning
- Delivers a final coordinated recommendation for the best city to visit

## Agent System Architecture

The application uses three specialized agents:

1. **Weather Researcher Agent (Amazon Bedrock Claude Haiku)**
   - Analyzes weather data for different cities in the selected state
   - Provides detailed information about current conditions and forecasts
   - Evaluates weather comfort levels

2. **Travel Advisor Agent (Amazon Bedrock Claude Sonnet)**
   - Recommends cities based on weather conditions
   - Considers factors like temperature, precipitation, and humidity
   - Provides detailed recommendations with reasoning

3. **Coordinator Agent (Amazon Bedrock Claude Haiku)**
   - Coordinates between the Weather Researcher and Travel Advisor
   - Summarizes findings and makes a final recommendation
   - Includes specific details about expected weather conditions

## Requirements

- Python 3.6+
- Strands Agents SDK
- OpenWeather API key
- AWS credentials configured for Amazon Bedrock access
- Streamlit (for web interface)

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```
4. Configure AWS credentials for Bedrock access:
   ```
   aws configure
   ```
5. Ensure you have access to Claude models in Amazon Bedrock:
   - Go to the AWS Bedrock console
   - Navigate to "Model access"
   - Request access to `anthropic.claude-3-haiku-20240307-v1` and `anthropic.claude-3-sonnet-20240229-v1`

## Usage

### Command Line Interface

Run the command-line application:

```
python travel_weather_app.py
```

You'll be prompted to enter a US state to analyze. The application will:
1. Identify major cities in the selected state
2. Determine Memorial Day weekend dates
3. Collect and analyze weather forecasts for each city
4. Generate travel recommendations based on weather data
5. Provide a final recommendation for the best city to visit

### Web Interface

Run the Streamlit web application:

```
streamlit run app.py
```

The web interface allows you to:
1. Select any US state from a dropdown menu
2. Run the multi-agent analysis with a single click
3. View detailed weather analysis and recommendations
4. Compare weather conditions between multiple cities
5. See visualizations of temperature and comfort scores

## Tools

The application includes several custom tools:

- `get_current_weather`: Retrieves current weather for a specified city in any state
- `get_forecast_weather`: Gets 5-day weather forecast for a city
- `get_us_states`: Returns a list of all US states
- `get_cities_by_state`: Returns a list of major cities in a specified state
- `get_memorial_day_info`: Provides Memorial Day weekend dates
- `analyze_weather_comfort`: Evaluates weather comfort based on temperature, humidity, and wind

## License

[MIT License](LICENSE)
