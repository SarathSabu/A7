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

# Default API Key 
DEFAULT_API_KEY = '78b9eee555a121cd1b49bfee825568e1'

# Streamlit app
st.title("Flight Tracker")

# Sidebar for user input
st.sidebar.header("Flight Information")
api_key = st.sidebar.text_input("Enter your API Key", value=DEFAULT_API_KEY)
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

            # Display live flight data if available
            if 'live' in flight_data and flight_data['live']:
                st.write("### Live Flight Data")
                live_data = flight_data['live']
                latitude = live_data.get('latitude')
                longitude = live_data.get('longitude')
                altitude = live_data.get('altitude', 'N/A')
                speed_horizontal = live_data.get('speed_horizontal', 'N/A')
                speed_vertical = live_data.get('speed_vertical', 'N/A')
                direction = live_data.get('direction', 'N/A')
                is_ground = live_data.get('is_ground', False)

                st.write(f"**Latitude:** {latitude}")
                st.write(f"**Longitude:** {longitude}")
                st.write(f"**Altitude:** {altitude} feet")
                st.write(f"**Speed (horizontal):** {speed_horizontal} km/h")
                st.write(f"**Speed (vertical):** {speed_vertical} km/h")
                st.write(f"**Direction:** {direction} degrees")
                st.write(f"**Is Grounded:** {'Yes' if is_ground else 'No'}")

                # Map showing the current position of the flight
                if latitude and longitude:
                    map_data = pd.DataFrame({
                        'lat': [latitude],
                        'lon': [longitude]
                    })

                    view_state = pdk.ViewState(
                        latitude=latitude,
                        longitude=longitude,
                        zoom=5,
                        pitch=0,
                    )

                    layer = pdk.Layer(
                        'ScatterplotLayer',
                        data=map_data,
                        get_position='[lon, lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=10000,
                    )

                    r = pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        tooltip={"text": "Current Position"},
                    )
                    st.pydeck_chart(r)
                else:
                    st.write("Live location data is not available.")
            else:
                st.write("Live flight data is not available.")
                st.write(f"Debug info: {flight_data}")
        else:
            st.write("No flight data found. Please check the flight number.")
            st.write(f"Debug info: {data}")
    else:
        st.write("Please enter a valid API key and flight number.")
