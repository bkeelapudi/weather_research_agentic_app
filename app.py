"""
US State Weather Travel Planner - Streamlit Web UI
This application uses Strands Agents SDK to find the best weather in any US state
for Memorial Day weekend using OpenWeather API and Amazon Bedrock models.
"""

import streamlit as st
import os
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from travel_weather_app import (
    get_current_weather, 
    get_forecast_weather, 
    get_us_states,
    get_cities_by_state,
    get_memorial_day_info,
    analyze_weather_comfort,
    weather_researcher,
    travel_advisor,
    coordinator,
    extract_recommended_city,
    run_multi_agent_system
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="US State Weather Travel Planner",
    page_icon="🌞",
    layout="wide"
)

# Header
st.title("🌞 US State Memorial Day Weekend Weather Finder")
st.markdown("Find the best weather in any US state for Memorial Day weekend using AI agents")

# Sidebar
st.sidebar.title("About")
st.sidebar.info(
    "This application uses multiple AI agents to analyze weather data "
    "and recommend the best city in any US state to visit during Memorial Day weekend. "
    "The agents work together to provide detailed analysis and recommendations."
)

st.sidebar.title("Agents")
st.sidebar.markdown("""
- **Weather Research Assistant**: Analyzes weather data for cities in the selected state (Amazon Bedrock Claude Haiku)
- **Travel Advisor**: Makes recommendations based on weather conditions (Amazon Bedrock Claude Sonnet)
- **Coordinator**: Synthesizes information and provides final recommendations (Amazon Bedrock Claude Haiku)
""")

# Main content
tab1, tab2, tab3 = st.tabs(["Run Analysis", "City Comparison", "About"])

with tab1:
    st.header("Find the Best Weather in Your Selected State")
    st.markdown("Select a US state and click the button to run the multi-agent analysis and find the best city to visit during Memorial Day weekend.")
    
    # State selection
    all_states = get_us_states()
    selected_state = st.selectbox("Select a US State", all_states, index=all_states.index("California") if "California" in all_states else 0)
    
    # Year selection
    year = st.selectbox("Select Year", [2025, 2026, 2027], index=0)
    
    # Run analysis button
    if st.button("Run Weather Analysis"):
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Get cities and Memorial Day info
        status_text.text(f"Getting cities in {selected_state}...")
        progress_bar.progress(10)
        cities = get_cities_by_state(selected_state)
        
        status_text.text("Getting Memorial Day weekend dates...")
        progress_bar.progress(20)
        memorial_day_info = get_memorial_day_info()
        
        # Display Memorial Day info
        st.subheader("Memorial Day Weekend Info")
        st.write(f"Start Date: {memorial_day_info['start_date']}")
        st.write(f"End Date: {memorial_day_info['end_date']}")
        
        # Step 2: Weather analysis
        status_text.text(f"Analyzing weather data for {selected_state} cities...")
        progress_bar.progress(30)
        
        # Create a placeholder for the weather analysis
        weather_analysis_placeholder = st.empty()
        
        # Select a subset of cities if there are too many
        if len(cities) > 8:
            selected_cities = cities[:8]  # Take the first 8 cities
        else:
            selected_cities = cities
        
        # Simulate the weather analysis process
        weather_data_prompt = f"""
        Please check the weather forecasts for these {selected_state} cities:
        - {", ".join(selected_cities)}
        
        Analyze which cities are likely to have the best weather for Memorial Day weekend.
        Consider temperature, precipitation chance, and overall conditions.
        Use the analyze_weather_comfort tool to evaluate each city's comfort level.
        """
        
        # Run the weather analysis
        weather_analysis = weather_researcher(weather_data_prompt)
        weather_analysis_placeholder.markdown(f"### Weather Analysis\n{weather_analysis}")
        progress_bar.progress(50)
        
        # Step 3: Travel recommendation
        status_text.text("Getting travel recommendations...")
        recommendation_prompt = f"""
        Based on this weather analysis:
        
        {weather_analysis}
        
        Which {selected_state} city would you recommend for a visit during Memorial Day weekend?
        Please explain your reasoning and provide details about why this location offers the best weather experience.
        Use the analyze_weather_comfort tool to evaluate your top recommendations.
        """
        
        travel_recommendation = travel_advisor(recommendation_prompt)
        progress_bar.progress(70)
        
        # Step 4: Final coordination
        status_text.text("Finalizing recommendation...")
        final_prompt = f"""
        Please review the weather analysis and travel recommendation:
        
        Weather Analysis:
        {weather_analysis}
        
        Travel Recommendation:
        {travel_recommendation}
        
        Provide a final summary and recommendation for the best city in {selected_state} to visit during 
        Memorial Day weekend {year} based on weather conditions. Include any additional considerations 
        travelers should keep in mind.
        """
        
        final_recommendation = coordinator(final_prompt)
        progress_bar.progress(90)
        
        # Extract recommended city
        recommended_city = extract_recommended_city(final_recommendation, cities)
        
        # Display results
        status_text.text("Analysis complete!")
        progress_bar.progress(100)
        
        # Display recommendation
        st.subheader("Travel Recommendation")
        st.markdown(travel_recommendation)
        
        st.subheader("Final Recommendation")
        st.markdown(final_recommendation)
        
        # Display recommended city with more prominence
        st.success(f"**Recommended City: {recommended_city}**")
        
        # Show the raw text for debugging
        with st.expander("Debug Information"):
            st.write("Raw final recommendation text:")
            if hasattr(final_recommendation, 'content'):
                st.code(final_recommendation.content)
            else:
                st.code(str(final_recommendation))
            
            st.write("City extraction process:")
            for city in cities:
                if city in str(final_recommendation):
                    st.write(f"- Found '{city}' in the recommendation")
        
        # Get current weather for the recommended city
        try:
            current_weather = get_current_weather(recommended_city, selected_state)
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Current Weather in {recommended_city}, {selected_state}")
                st.write(f"Temperature: {current_weather['temperature']}")
                st.write(f"Feels Like: {current_weather['feels_like']}")
                st.write(f"Conditions: {current_weather['conditions']}")
                st.write(f"Humidity: {current_weather['humidity']}")
                st.write(f"Wind: {current_weather['wind']}")
                st.write(f"Pressure: {current_weather['pressure']}")
            
            with col2:
                # Create a simple gauge chart for temperature
                fig, ax = plt.subplots(figsize=(4, 4))
                temp = float(current_weather['temperature'].replace('°C', ''))
                sns.barplot(x=['Temperature'], y=[temp], ax=ax)
                ax.set_ylim(0, 40)
                ax.set_title(f"Temperature in {recommended_city}")
                ax.set_ylabel("°C")
                st.pyplot(fig)
        
        except Exception as e:
            st.error(f"Error getting current weather: {str(e)}")

with tab2:
    st.header("Compare Cities")
    
    # State selection for comparison
    comparison_state = st.selectbox("Select a US State for comparison", all_states, index=all_states.index("California") if "California" in all_states else 0, key="comparison_state")
    
    # Get cities for the selected state
    state_cities = get_cities_by_state(comparison_state)
    
    # Select cities to compare
    cities_to_compare = st.multiselect(
        "Select cities to compare",
        state_cities,
        default=state_cities[:4] if len(state_cities) >= 4 else state_cities
    )
    
    if st.button("Compare Selected Cities"):
        if not cities_to_compare:
            st.warning("Please select at least one city to compare.")
        else:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Get weather data for each city
            weather_data = {}
            for i, city in enumerate(cities_to_compare):
                status_text.text(f"Getting weather data for {city}, {comparison_state}...")
                progress_bar.progress((i + 1) / len(cities_to_compare))
                
                try:
                    current = get_current_weather(city, comparison_state)
                    weather_data[city] = {
                        'temperature': float(current['temperature'].replace('°C', '')),
                        'humidity': float(current['humidity'].replace('%', '')),
                        'wind': float(current['wind'].replace(' m/s', '')),
                        'conditions': current['conditions']
                    }
                except Exception as e:
                    st.error(f"Error getting weather data for {city}: {str(e)}")
            
            # Create a DataFrame for comparison
            if weather_data:
                df = pd.DataFrame.from_dict(weather_data, orient='index')
                
                # Display the data
                st.subheader("Current Weather Comparison")
                st.dataframe(df)
                
                # Create charts
                st.subheader("Temperature Comparison")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=df.index, y='temperature', data=df, ax=ax)
                ax.set_ylabel("Temperature (°C)")
                ax.set_title("Temperature Comparison")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
                # Comfort analysis
                st.subheader("Weather Comfort Analysis")
                comfort_scores = {}
                for city, data in weather_data.items():
                    comfort = analyze_weather_comfort(
                        data['temperature'],
                        data['humidity'],
                        data['wind']
                    )
                    comfort_scores[city] = {
                        'comfort_score': comfort['comfort_score'],
                        'comfort_level': comfort['comfort_level'],
                        'temperature_score': comfort['temperature_score'],
                        'humidity_score': comfort['humidity_score'],
                        'wind_score': comfort['wind_score']
                    }
                
                # Create a DataFrame for comfort scores
                comfort_df = pd.DataFrame.from_dict(comfort_scores, orient='index')
                st.dataframe(comfort_df)
                
                # Create a chart for comfort scores
                st.subheader("Overall Comfort Score Comparison")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=comfort_df.index, y='comfort_score', data=comfort_df, ax=ax)
                ax.set_ylabel("Comfort Score (0-100)")
                ax.set_title("Weather Comfort Score Comparison")
                plt.xticks(rotation=45)
                st.pyplot(fig)

with tab3:
    st.header("About This Application")
    st.markdown("""
    ## US State Weather Travel Planner
    
    This application helps you find the best weather in any US state for Memorial Day weekend using the Strands Agents SDK and OpenWeather API.
    
    ### How It Works
    
    1. **Weather Research Assistant**: Analyzes weather data for major cities in your selected state
    2. **Travel Advisor**: Makes recommendations based on weather conditions
    3. **Coordinator**: Synthesizes information and provides final recommendations
    
    ### Technologies Used
    
    - **Strands Agents SDK**: For creating and managing AI agents
    - **Amazon Bedrock**: For powering the AI models (Titan and Claude)
    - **OpenWeather API**: For fetching real-time weather data
    - **Streamlit**: For creating the web interface
    
    ### Created By
    
    This application was created as a demonstration of multi-agent AI systems for travel planning.
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 US State Weather Travel Planner | Powered by Strands Agents SDK, Amazon Bedrock, and OpenWeather API")
