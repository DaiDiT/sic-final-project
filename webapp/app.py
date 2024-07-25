import streamlit as st
import requests
import time
from datetime import datetime

st.title("Air Quality Prediction")
st.write("Air quality is a critical factor in ensuring a healthy environment. This app allows you to view real-time air quality data and predict air quality based on your own input data.")

st.header("Realtime Data from Our IoT Device")

if 'status_color' not in st.session_state:
    st.session_state.status_color = "red"
if 'status_text' not in st.session_state:
    st.session_state.status_text = "Offline"
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0
if 'humidity' not in st.session_state:
    st.session_state.humidity = 0
if 'co' not in st.session_state:
    st.session_state.co = 0
if 'co2' not in st.session_state:
    st.session_state.co2 = 0
if 'air_quality' not in st.session_state:
    st.session_state.air_quality = "Good"
if 'predict' not in st.session_state:
    st.session_state.predict = False

st.markdown(
    f"""
    Device Status:
    <div style="display: flex; align-items: center;">
        <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {st.session_state.status_color}; margin-right: 8px;"></div>
        <span style="font-size: 16px;">{st.session_state.status_text}</span>
    </div>
    <br>
    """,
    unsafe_allow_html=True
)


def fetch_data_from_api():
    try:
        response = requests.get('http://localhost:8000/api/v1/sic5/sensor-data')
        response.raise_for_status()
        data = response.json()
        new_temperature = data['temperature']
        new_humidity = data['humidity']
        new_co = data['co']
        new_co2 = data['co2']
        last_updated = datetime.strptime(data['timestamp'], "%a, %d %b %Y %H:%M:%S %Z")
        current_time = datetime.now()
        time_difference = (current_time - last_updated).total_seconds()

        if time_difference < 15:
            st.session_state.status_color = "green"
            st.session_state.status_text = "Online"
        else:
            st.session_state.status_color = "red"
            st.session_state.status_text = "Offline"
        
        temperature_delta = new_temperature - st.session_state.temperature
        humidity_delta = new_humidity - st.session_state.humidity
        co_delta = new_co - st.session_state.co
        co2_delta = new_co2 - st.session_state.co2

        st.session_state.temperature = new_temperature
        st.session_state.humidity = new_humidity
        st.session_state.co = new_co
        st.session_state.co2 = new_co2
        st.session_state.last_update_time = current_time

        return temperature_delta, humidity_delta, co_delta, co2_delta
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None, None, None, None

temperature_delta, humidity_delta, co_delta, co2_delta = fetch_data_from_api()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Temperature", value=f"{st.session_state.temperature} °C", delta=f"{temperature_delta} °C")
    st.metric(label="CO", value=f"{st.session_state.co} ppm", delta=f"{co_delta} ppm")
with col2:
    st.metric(label="Humidity", value=f"{st.session_state.humidity} %", delta=f"{humidity_delta} %")
    st.metric(label="CO2", value=f"{st.session_state.co2} ppm", delta=f"{co2_delta} ppm")

st.metric(label="Air Quality", value=st.session_state.air_quality)
st.header("Predict Your Own Data")
colf1, colf2, colf3, colf4 = st.columns(4)

if 'input_temperature' not in st.session_state:
    st.session_state.input_temperature = 25
if 'input_humidity' not in st.session_state:
    st.session_state.input_humidity = 50
if 'input_co' not in st.session_state:
    st.session_state.input_co = 10
if 'input_co2' not in st.session_state:
    st.session_state.input_co2 = 400

st.session_state.input_temperature = colf1.number_input(
    "Temperature (°C)", min_value=-50, max_value=50, value=st.session_state.input_temperature)
st.session_state.input_humidity = colf2.number_input(
    "Humidity (%)", min_value=0, max_value=100, value=st.session_state.input_humidity)
st.session_state.input_co = colf3.number_input(
    "CO (ppm)", min_value=0, max_value=1000, value=st.session_state.input_co)
st.session_state.input_co2 = colf4.number_input(
    "CO2 (ppm)", min_value=0, max_value=5000, value=st.session_state.input_co2)

def predict_air_quality():
    if st.session_state.input_temperature > 35 or st.session_state.input_co > 300 or st.session_state.input_co2 > 1000:
        st.session_state.air_quality = "Poor"
    elif st.session_state.input_humidity > 80:
        st.session_state.air_quality = "Moderate"
    else:
        st.session_state.air_quality = "Good"

if st.button("Predict"):
    st.session_state.predict = True
    predict_air_quality()

if st.session_state.predict:
    st.write(f"Predicted Air Quality: {st.session_state.room_quality}")

while True:
    time.sleep(10)
    fetch_data_from_api()