import streamlit as st
import requests
import time
import pytz
from datetime import datetime
from predict import predict_air_quality

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Predict"])

if page == "Home":
    st.title("Indoor Air Quality Prediction")
    st.write("Air quality is a critical factor in ensuring a healthy environment. This app allows you to view real-time air quality data and predict air quality based on your own input data.")

    st.text("")

    st.subheader("Realtime Data from Our IoT Device")

    if 'status_color' not in st.session_state:
        st.session_state.status_color = "red"
    if 'status_text' not in st.session_state:
        st.session_state.status_text = "Offline"
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.0
    if 'temperature_delta' not in st.session_state:
        st.session_state.temperature_delta = 0.0
    if 'humidity' not in st.session_state:
        st.session_state.humidity = 0
    if 'humidity_delta' not in st.session_state:
        st.session_state.humidity_delta = 0
    if 'co' not in st.session_state:
        st.session_state.co = 0
    if 'co_delta' not in st.session_state:
        st.session_state.co_delta = 0
    if 'air_quality' not in st.session_state:
        st.session_state.air_quality = ""

    def fetch_data_from_api():
        try:
            response = requests.get('https://esp32-flask.vercel.app/api/v1/sic5/sensor-data')
            response.raise_for_status()
            data = response.json()
            new_temperature = data['temperature']
            new_humidity = data['humidity']
            new_co = data['CO']
            new_air_quality = predict_air_quality(new_temperature, new_humidity, new_co)
            last_updated = datetime.strptime(data['timestamp'], "%a, %d %b %Y %H:%M:%S %Z")
            last_updated = pytz.utc.localize(last_updated)
            current_time = datetime.now(pytz.utc)
            time_difference = (current_time - last_updated).total_seconds()
            
            if time_difference < 30:
                st.session_state.status_color = "green"
                st.session_state.status_text = "Online"
            else:
                st.session_state.status_color = "red"
                st.session_state.status_text = "Offline"

            print(time_difference)
            
            st.session_state.temperature_delta = round(new_temperature - st.session_state.temperature, 1)
            st.session_state.humidity_delta = round(new_humidity - st.session_state.humidity, 1)
            st.session_state.co_delta = round(new_co - st.session_state.co, 1)

            st.session_state.temperature = new_temperature
            st.session_state.humidity = new_humidity
            st.session_state.co = new_co
            st.session_state.air_quality = new_air_quality
            st.session_state.last_update_time = current_time
        
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data from API: {e}")

    fetch_data_from_api()

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

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Temperature", value=f"{st.session_state.temperature} °C", delta=f"{st.session_state.temperature_delta} °C")
        st.metric(label="CO", value=f"{st.session_state.co} ppm", delta=f"{st.session_state.co_delta} ppm")
    with col2:
        st.metric(label="Humidity", value=f"{st.session_state.humidity} %", delta=f"{st.session_state.humidity_delta} %")
        st.metric(label="Air Quality", value=st.session_state.air_quality)

    time.sleep(10)
    st.rerun()

elif page == "Predict":
    if 'message' not in st.session_state:
        st.session_state.message = ""
    if 'predicted_air_quality' not in st.session_state:
        st.session_state.predicted_air_quality = ""
    if 'predict' not in st.session_state:
        st.session_state.predict = False

    st.header("Predict Air Quality")
    colf1, colf2, colf3, colf4 = st.columns(4)

    if 'input_temperature' not in st.session_state:
        st.session_state.input_temperature = 25
    if 'input_humidity' not in st.session_state:
        st.session_state.input_humidity = 50
    if 'input_co' not in st.session_state:
        st.session_state.input_co = 10

    st.session_state.input_temperature = colf1.number_input(
        "Temperature (°C)", min_value=-50, max_value=50, value=st.session_state.input_temperature)
    st.session_state.input_humidity = colf2.number_input(
        "Humidity (%)", min_value=0, max_value=100, value=st.session_state.input_humidity)
    st.session_state.input_co = colf3.number_input(
        "CO (ppm)", min_value=0, max_value=1000, value=st.session_state.input_co)

    if st.button("Predict"):
        st.session_state.predict = True
        with st.spinner('Processing data...'):
            time.sleep(3)
            st.session_state.predicted_air_quality = predict_air_quality(
                st.session_state.input_temperature, 
                st.session_state.input_humidity, 
                st.session_state.input_co
            )
            if st.session_state.predicted_air_quality == "Good":
                st.session_state.message = ":slightly_smiling_face: Enjoy your activities safely."
            elif st.session_state.predicted_air_quality == "Moderate":
                st.session_state.message = ":warning: If there's smoke in the room, consider leaving the area."
            else:
                st.session_state.message = ":no_entry: It's best not to stay in this room for an extended period."

    if st.session_state.predict:
        st.write(f"Air Quality: {st.session_state.predicted_air_quality}")
        st.write(f"Message: {st.session_state.message}")