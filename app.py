import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# Function to fetch flight data
def fetch_flight_data(api_key, flight_number):
    url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&flight_iata={flight_number}"
    response = requests.get(url)
    data = response.json()
    return data

# Default API Key (make sure to replace 'your_default_api_key' with your actual API key)
DEFAULT_API_KEY = 'your_default_api_key'

# Streamlit app
st.title("Flight Tracker App")

# Sidebar for user input
st.sidebar.header("Flight Information")
api_key = st.sidebar.text_input("Enter your API Key", value= "45a49177587200a61137f0067c01b0fb" )
flight_number = st.sidebar.text_input("Enter Flight Number (IATA Code)")

if st.sidebar.button("Track Flight"):
    if api_key and flight_number:
        data = fetch_flight_data(api_key, flight_number)
        if data and 'data' in data and data['data']:
            flight_data = data['data'][0]
            st.write(f"### Flight {flight_number} Information")
            st.write(f"**Airline:** {flight_data['airline']['name']}")
            st.write(f"**Flight Number:** {flight_data['flight']['iata']}")
            st.write(f"**Departure:** {flight_data['departure']['airport']} at {flight_data['departure']['scheduled']}")
            st.write(f"**Arrival:** {flight_data['arrival']['airport']} at {flight_data['arrival']['scheduled']}")
            st.write(f"**Status:** {flight_data['flight_status']}")

            # Displaying map with default locations if latitude and longitude are missing
            dep_lat = flight_data['departure'].get('estimated_runway_lat', 0)
            dep_lon = flight_data['departure'].get('estimated_runway_lon', 0)
            arr_lat = flight_data['arrival'].get('estimated_runway_lat', 0)
            arr_lon = flight_data['arrival'].get('estimated_runway_lon', 0)

            # Functional map using pydeck
            map_data = pd.DataFrame({
                'lat': [dep_lat, arr_lat],
                'lon': [dep_lon, arr_lon]
            })

            if dep_lat and dep_lon and arr_lat and arr_lon:
                view_state = pdk.ViewState(
                    latitude=(dep_lat + arr_lat) / 2,
                    longitude=(dep_lon + arr_lon) / 2,
                    zoom=3,
                    pitch=0,
                )

                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=map_data,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100000,
                )

                r = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "Flight Location"},
                )
                st.pydeck_chart(r)

            # Display live flight data if available
            if 'live' in flight_data and flight_data['live']:
                st.write("### Live Flight Data")
                live_data = flight_data['live']
                st.write(f"**Latitude:** {live_data.get('latitude', 'N/A')}")
                st.write(f"**Longitude:** {live_data.get('longitude', 'N/A')}")
                st.write(f"**Altitude:** {live_data.get('altitude', 'N/A')} feet")
                st.write(f"**Speed (horizontal):** {live_data.get('speed_horizontal', 'N/A')} km/h")
                st.write(f"**Speed (vertical):** {live_data.get('speed_vertical', 'N/A')} km/h")
                st.write(f"**Direction:** {live_data.get('direction', 'N/A')} degrees")
                st.write(f"**Is Grounded:** {'Yes' if live_data.get('is_ground', False) else 'No'}")
        else:
            st.write("No flight data found. Please check the flight number.")
    else:
        st.write("Please enter a valid API key and flight number.")