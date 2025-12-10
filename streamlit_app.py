
import os
import json
import requests
import streamlit as st
from datetime import datetime
from statistics import mean
from streamlit_lottie import st_lottie

# Page config
st.set_page_config(page_title="Weather • OpenWeather", page_icon="🌤", layout="centered")

# --- Language toggle ---
lang_label = st.radio("Language / Langue", ["English", "Français"], horizontal=True)
lang = "en" if lang_label == "English" else "fr"

# --- Localized UI strings ---
TEXT = {
    "en": {
        "title": "🌤 Weather App",
        "subtitle": "Enter a city to get current weather (OpenWeather API).",
        "city_input": "City name",
        "city_ph": "e.g., Montreal, Paris, Tokyo",
        "units": "Units",
        "fetching_weather": "Fetching weather…",
        "local_obs": "Local observation",
        "temp": "Temperature",
        "feels_like": "Feels like",
        "humidity": "Humidity",
        "wind": "Wind",
        "pressure": "Pressure",
        "location": "📍 Location",
        "begin": "Type a city to begin.",
        "could_not_fetch": "Could not fetch weather for",
        "details": "Details",
        "raw_current": "Show raw current weather (JSON)",
        "forecast_title": "🗓 5‑day forecast",
        "fetching_forecast": "Fetching forecast…",
        "forecast_unavailable": "Forecast data is unavailable right now.",
        "highlow": "High/Low",
        "avg_wind": "Avg wind",
        "precip": "Precip",
        "unknown_error": "Unknown error"
    },
    "fr": {
        "title": "🌤 Application Météo",
        "subtitle": "Entrez une ville pour obtenir la météo actuelle (API OpenWeather).",
        "city_input": "Nom de la ville",
        "city_ph": "ex. : Montréal, Paris, Tokyo",
        "units": "Unités",
        "fetching_weather": "Récupération de la météo…",
        "local_obs": "Observation locale",
        "temp": "Température",
        "feels_like": "Ressentie",
        "humidity": "Humidité",
        "wind": "Vent",
        "pressure": "Pression",
        "location": "📍 Localisation",
        "begin": "Saisissez une ville pour commencer.",
        "could_not_fetch": "Impossible de récupérer la météo pour",
        "details": "Détails",
        "raw_current": "Afficher les données météo brutes (JSON)",
        "forecast_title": "🗓 Prévisions sur 5 jours",
        "fetching_forecast": "Récupération des prévisions…",
        "forecast_unavailable": "Les données de prévision ne sont pas disponibles pour le moment.",
        "highlow": "Max/Min",
        "avg_wind": "Vent moyen",
        "precip": "Précip.",
        "unknown_error": "Erreur inconnue"
    }
}
t = TEXT[lang]

# --- UI ---
st.title(t["title"])
st.caption(t["subtitle"])
city = st.text_input(t["city_input"], placeholder=t["city_ph"])

# Units
unit_label = st.radio(t["units"], ["°C", "°F"], horizontal=True)
units = "metric" if unit_label == "°C" else "imperial"
temp_unit = "°C" if units == "metric" else "°F"
wind_unit = "m/s" if units == "metric" else "mph"

# Secrets
API_KEY = st.secrets["API_KEY"]
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

@st.cache_data(ttl=300)
def fetch_weather(city_name: str, api_key: str, units: str = "metric", lang: str = "en"):
    params = {"q": city_name, "appid": api_key, "units": units, "lang": lang}
    return requests.get(CURRENT_URL, params=params)

@st.cache_data(ttl=600)
def fetch_forecast(city_name: str, api_key: str, units: str = "metric", lang: str = "en"):
    params = {"q": city_name, "appid": api_key, "units": units, "lang": lang}
    return requests.get(FORECAST_URL, params=params)

def badge_color(main: str) -> str:
    main = (main or "").lower()
    if main in ["clear"]: return "#f6c453"
    if main in ["clouds"]: return "#9aa5b1"
    if main in ["rain", "drizzle"]: return "#5aa9e6"
    if main in ["thunderstorm"]: return "#4b5563"
    if main in ["snow"]: return "#cfe9ff"
    if main in ["mist", "fog", "haze", "smoke"]: return "#cbd5e1"
    return "#e5e7eb"

# ---------- Animated icon utilities ----------
LOTTIE_DIR = os.path.join(os.path.dirname(__file__), "assets", "lottie")

# Map OpenWeather "main" + day/night to a local Lottie file
ICON_MAP = {
    "clear_day": "clear-day.json",
    "clear_night": "clear-night.json",
    "clouds": "clouds.json",
    "rain": "rain.json",
    "drizzle": "rain.json",
    "thunderstorm": "thunder.json",
    "snow": "snow.json",
    "mist": "mist.json",
    "fog": "mist.json",
    "haze": "mist.json",
    "smoke": "mist.json",
}

@st.cache_data
def load_lottie_from_file(filename: str):
    """Load a Lottie JSON from the assets folder; return dict or None."""
    path = os.path.join(LOTTIE_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def get_lottie_asset(condition_main: str, icon_code: str):
    """
    Decide which animation to show based on condition and day/night.
    icon_code ends with 'd' or 'n' (day/night) from OpenWeather (e.g., '01d', '10n').
    """
    is_day = (icon_code or "d").endswith("d")
    key = (condition_main or "").lower()

    if key == "clear":
        filename = ICON_MAP["clear_day"] if is_day else ICON_MAP["clear_night"]
    else:
        filename = ICON_MAP.get(key)

    if filename:
        return load_lottie_from_file(filename)
    return None
# ---------------------------------------------

def summarize_daily_forecast(forecast_json: dict):
    """Aggregate 3-hour forecast into daily summaries."""
    if not forecast_json or "list" not in forecast_json:
        return []

    tz = forecast_json.get("city", {}).get("timezone", 0)  # seconds offset
    from collections import defaultdict
    buckets = defaultdict(list)

    for item in forecast_json["list"]:
        dt = item.get("dt")
        if dt is None:
            continue
        local_dt = datetime.utcfromtimestamp(dt + tz)
        day_key = local_dt.date().isoformat()
        buckets[day_key].append((local_dt, item))

    summaries = []
    for day, entries in sorted(buckets.items()):
        highs  = [e[1].get("main", {}).get("temp_max") for e in entries if e[1].get("main", {})]
        lows   = [e[1].get("main", {}).get("temp_min") for e in entries if e[1].get("main", {})]
        winds  = [e[1].get("wind", {}).get("speed")    for e in entries if e[1].get("wind", {})]
        precip = 0.0
        for _, e in entries:
            precip += float(e.get("rain", {}).get("3h", 0) or 0)
            precip += float(e.get("snow", {}).get("3h", 0) or 0)

        # Representative icon/description closest to 12:00 local
        def hour_diff(h): return abs(h - 12)
        entries_sorted = sorted(entries, key=lambda x: hour_diff(x[0].hour))
        rep_weather = (entries_sorted[0][1].get("weather", [{}])[0]) if entries_sorted else {}
        description = (rep_weather.get("description") or "—").capitalize()
        icon_code = rep_weather.get("icon", "01d")
        condition_main = rep_weather.get("main", "")

        # Animated icon for the day
        lottie = get_lottie_asset(condition_main, icon_code)
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        summaries.append({
            "date": day,
            "high": (max(highs) if highs else None),
            "low":  (min(lows) if lows else None),
            "wind_avg": (round(mean(winds), 1) if winds else None),
            "precip_sum": round(precip, 1),
            "description": description,
            "lottie": lottie,
            "icon_url": icon_url
        })

    return summaries[:5]

# --- Display logic ---
if city:
    with st.spinner(t["fetching_weather"]):
        resp_current = fetch_weather(city, API_KEY, units=units, lang=lang)

    if resp_current.status_code == 200:
        data = resp_current.json()

        name = data.get("name", city)
        country = data.get("sys", {}).get("country", "")
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [])
        w0 = weather_list[0] if weather_list else {}
        description = (w0.get("description", "—") or "—").capitalize()
        condition_main = w0.get("main", "")
        icon_code = w0.get("icon", "01d")
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        # Load animated icon for current conditions
        lottie_current = get_lottie_asset(condition_main, icon_code)

        temp = main.get("temp", "—")
        feels_like = main.get("feels_like", "—")
        humidity = main.get("humidity", "—")
        pressure = main.get("pressure", "—")
        wind_speed = wind.get("speed", "—")

        dt = data.get("dt")
        tz = data.get("timezone", 0)
        local_dt = datetime.utcfromtimestamp(dt + tz) if isinstance(dt, (int, float)) else None

        # Header with animated icon + badge
        col_icon, col_title = st.columns([1, 3], vertical_alignment="center")
        with col_icon:
            if lottie_current:
                st_lottie(lottie_current, height=110, key=f"current-{icon_code}")
            else:
                st.image(icon_url, width=100)
        with col_title:
            st.subheader(f"Weather in {name}{' (' + country + ')' if country else ''}")
            if local_dt:
                st.caption(f"{t['local_obs']}: {local_dt.strftime('%d %b %Y, %H:%M')}")
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
        c1.metric(f"{t['temp']} ({temp_unit})", f"{temp}")
        c2.metric(f"{t['feels_like']} ({temp_unit})", f"{feels_like}")
        c3.metric(f"{t['humidity']} (%)", f"{humidity}")

        c4, c5 = st.columns(2)
        c4.metric(f"{t['wind']} ({wind_unit})", f"{wind_speed}")
        c5.metric(f"{t['pressure']} (hPa)", f"{pressure}")

        # Map
        coord = data.get("coord", {})
        if "lat" in coord and "lon" in coord:
            st.markdown(f"### {t['location']}")
            st.map(data=[{"lat": coord["lat"], "lon": coord["lon"]}], zoom=10)

        # --- 5-day forecast section ---
        st.markdown(f"## {t['forecast_title']}")
        with st.spinner(t["fetching_forecast"]):
            resp_fc = fetch_forecast(city, API_KEY, units=units, lang=lang)

        if resp_fc.status_code == 200:
            fc_json = resp_fc.json()
            daily = summarize_daily_forecast(fc_json)

            if not daily:
                st.info(t["forecast_unavailable"])
            else:
                cols = st.columns(len(daily))
                for col, d in zip(cols, daily):
                    with col:
                        st.markdown(f"**{d['date']}**")
                        # Animated icon or PNG
                        if d["lottie"]:
                            st_lottie(d["lottie"], height=90, key=f"fc-{d['date']}")
                        else:
                            st.image(d["icon_url"], width=80)
                        st.caption(d["description"])
                        hi = "—" if d["high"] is None else f"{round(d['high'])}"
                        lo = "—" if d["low"]  is None else f"{round(d['low'])}"
                        st.write(f"**{t['highlow']}:** {hi}/{lo} {temp_unit}")
                        wind_txt = "—" if d["wind_avg"] is None else f"{d['wind_avg']} {wind_unit}"
                        st.write(f"**{t['avg_wind']}:** {wind_txt}")
                        st.write(f"**{t['precip']}:** {d['precip_sum']} mm")
        else:
            msg = t["unknown_error"]
            try:
                msg = resp_fc.json().get("message", msg)
            except Exception:
                pass
            st.error(f"{t['could_not_fetch']} “{city}”. {t['details']}: {msg}")

        # Optional: raw JSON (current)
        with st.expander(t["raw_current"]):
            st.json(data)

    else:
        msg = t["unknown_error"]
        try:
            msg = resp_current.json().get("message", msg)
        except Exception:
            pass
        st.error(f"{t['could_not_fetch']} “{city}”. {t['details']}: {msg}")

else:
    st.info(t["begin"])
