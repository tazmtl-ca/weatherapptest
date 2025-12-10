
import streamlit as st
import requests
from datetime import datetime

# -----------------------------
# Configuration de la page
# -----------------------------
st.set_page_config(page_title="Météo • OpenWeather", page_icon="🌤", layout="centered")

# Titre et sous-titre
st.title("🌤 Application Météo")
st.caption("Entrez une ville pour obtenir la météo actuelle (OpenWeather API).")

# Champ de saisie
city = st.text_input("Nom de la ville", placeholder="Ex. : Montréal, Paris, Tokyo")

# Vos infos API
API_KEY = "YOUR_API_KEY"  # <-- Remplacez par votre clé OpenWeather
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Petite fonction utilitaire
def get_weather(city_name: str):
    url = f"{BASE_URL}?q={city_name}&appid={API_KEY}&units=metric&lang=fr"
    return requests.get(url)

# Palette de couleurs pour badges
def condition_color(main: str) -> str:
    main = (main or "").lower()
    if main in ["clear"]:
        return "#f6c453"   # ensoleillé
    if main in ["clouds"]:
        return "#9aa5b1"   # nuageux
    if main in ["rain", "drizzle"]:
        return "#5aa9e6"   # pluie
    if main in ["thunderstorm"]:
        return "#4b5563"   # orage
    if main in ["snow"]:
        return "#cfe9ff"   # neige
    if main in ["mist", "fog", "haze", "smoke"]:
        return "#cbd5e1"   # brume
    return "#e5e7eb"       # défaut

# Illustration et résultats
if city:
    with st.spinner("Récupération des données météo…"):
        response = get_weather(city)

    if response.status_code == 200:
        data = response.json()

        # Parsing des champs utiles
        name = data.get("name", city)
        sys = data.get("sys", {})
        country = sys.get("country", "")
        main_block = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [])
        weather0 = weather_list[0] if weather_list else {}
        description = weather0.get("description", "—").capitalize()
        condition_main = weather0.get("main", "")
        icon_code = weather0.get("icon", "01d")
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        temp = main_block.get("temp", "—")
        feels_like = main_block.get("feels_like", "—")
        humidity = main_block.get("humidity", "—")
        pressure = main_block.get("pressure", "—")
        wind_speed = wind.get("speed", "—")

        # Heure locale (si disponible)
        dt = data.get("dt")
        timezone = data.get("timezone", 0)
        local_dt = datetime.utcfromtimestamp(dt + timezone) if dt else None

        # En-tête avec icône
        col_icon, col_title = st.columns([1, 3], vertical_alignment="center")
        with col_icon:
            st.image(icon_url, width=100)
        with col_title:
            st.subheader(f"Météo à {name}{' (' + country + ')' if country else ''}")
            if local_dt:
                st.caption(f"Observation locale : {local_dt.strftime('%d %b %Y, %H:%M')}")
            badge_color = condition_color(condition_main)
            st.markdown(
                f"""
                <div style="
                    display:inline-block;
                    padding:6px 10px;
                    border-radius:12px;
                    background:{badge_color};
                    color:#111827;
                    font-weight:600;
                    margin-top:6px;
                ">
                    {description}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Métriques principales
        c1, c2, c3 = st.columns(3)
        c1.metric("Température (°C)", f"{temp}")
        c2.metric("Ressentie (°C)", f"{feels_like}")
        c3.metric("Humidité (%)", f"{humidity}")

        c4, c5 = st.columns(2)
        c4.metric("Vent (m/s)", f"{wind_speed}")
        c5.metric("Pression (hPa)", f"{pressure}")

        # Carte si coordonnées disponibles
        coord = data.get("coord", {})
        if "lat" in coord and "lon" in coord:
            st.markdown("### 📍 Localisation")
            st.map(data=[{"lat": coord["lat"], "lon": coord["lon"]}], zoom=10)

        # Détails bruts (optionnel)
        with st.expander("Voir les données brutes (JSON)"):
            st.json(data)

    else:
        # Gestion d’erreur (ville introuvable, clé invalide, etc.)
        try:
            err = response.json()
            msg = err.get("message", "Erreur")
        except Exception:
            msg = f"Erreur HTTP {response.status_code}"
        st.error(f"Impossible de récupérer la météo pour « {city} ». Détails : {msg}")
else:
    st.info("Saisissez une ville pour commencer.")
