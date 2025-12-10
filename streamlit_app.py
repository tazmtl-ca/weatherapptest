
import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(page_title="Weather • OpenWeather", page_icon="🌤", layout="centered")

st.title("🌤 Weather App")
st.caption("Enter a city to get current weather (OpenWeather API).")

# Input
city = st.text_input("City name", placeholder="e.g., Montreal, Paris, Tokyo")

# Read API key from Streamlit Secrets (Settings → Secrets in Streamlit Cloud)
# Make sure your secrets contain: API_KEY = "your_openweather_api_key"
API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@st.cache_data(ttl=300)
def fetch_weather(city_name: str, api_key: str, units: str = "metric", lang: str = "en"):
    params = {"q": city_name, "appid": api_key, "units": units, "lang": lang}
    return requests.get(BASE_URL, params=params)

def badge_color(main: str) -> str:
    main = (main or "").lower()
    if main in ["clear"]: return "#f6c453"
    if main in ["clouds"]: return "#9aa5b1"
    if main in ["rain", "drizzle"]: return "#5aa9e6"
    if main in ["thunderstorm"]: return "#4b5563"
    if main in ["snow"]: return "#cfe9ff"
    if main in ["mist", "fog", "haze", "smoke"]: return "#cbd5e1"
    return "#e5e7eb"

if city:
    with st.spinner("Fetching weather…"):
        resp = fetch_weather(city, API_KEY, units="metric", lang="en")

    if resp.status_code == 200:
        data = resp.json()

        name = data.get("name", city)
        country = data.get("sys", {}).get("country", "")
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [])
        w0 = weather_list[0] if weather_list else {}
        description = w0.get("description", "—").capitalize()
        condition_main = w0.get("main", "")
        icon_code = w0.get("icon", "01d")
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        temp = main.get("temp", "—")
        feels_like = main.get("feels_like", "—")
        humidity = main.get("humidity", "—")
        pressure = main.get("pressure", "—")
        wind_speed = wind.get("speed", "—")

        dt = data.get("dt")
        tz = data.get("timezone", 0)
        local_dt = datetime.utcfromtimestamp(dt + tz) if dt is not None else None

        # Header with icon
        col_icon, col_title = st.columns([1, 3], vertical_alignment="center")
        with col_icon:
            st.image(icon_url, width=100)
        with col_title:
            st.subheader(f"Weather in {name}{' (' + country + ')' if country else ''}")
            if local_dt:
                st.caption(f"Local observation: {local_dt.strftime('%d %b %Y, %H:%M')}")
            st.markdown(
                f"""
                <div style="
                    display:inline-block;padding:6px 10px;border-radius:12px;
                    background:{badge_color(condition_main)};color:#111827;
                    font-weight:600;margin-top:6px;">
                    {description}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature (°C)", f"{temp}")
        c2.metric("Feels like (°C)", f"{feels_like}")
        c3.metric("Humidity (%)", f"{humidity}")

        c4, c5 = st.columns(2)
        c4.metric("Wind (m/s)", f"{wind_speed}")
        c5.metric("Pressure (hPa)", f"{pressure}")

        # Map
        coord = data.get("coord", {})
        if "lat" in coord and "lon" in coord:
            st.markdown("### 📍 Location")
            st.map(data=[{"lat": coord["lat"], "lon": coord["lon"]}], zoom=10)

        # Optional: raw JSON
        with st.expander("Show raw data (JSON)"):
            st.json(data)

    else:
        # Try to show API error message
        msg = "Unknown error"
        try:
            msg = resp.json().get("message", msg)
        except Exception:
            pass
        st.error(f"Could not fetch weather for “{city}”. Details: {msg}")

else:
    st.info("Type a city to begin.")
