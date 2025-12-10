
# Lottie Weather Starter Pack (Structure & Tools)

This pack gives you a ready-to-use folder structure, a mapping template, and a helper script to
download animated Lottie JSON files for common weather conditions (clear day/night, clouds,
rain/drizzle, thunderstorm, snow, mist/fog/haze/smoke).

## What’s inside
- `assets/lottie/` — put your downloaded `.json` animations here (e.g., `clear-day.json`).
- `mapping_example.json` — a template mapping weather conditions to local filenames and/or URLs.
- `download_lotties.py` — helper script to download Lottie JSONs from URLs into `assets/lottie/`.

## Where to find free animated weather Lotties
- LottieFiles Weather Icons collection: https://lottiefiles.com/free-animations/weather-icons
- IconScout Weather Lottie Animations: https://iconscout.com/lottie-animations/weather
- Creattie Weather Lottie Animated Icons: https://creattie.com/lottie-animated-icons/Weather

Please check the license for each asset you download and comply with attribution/usage terms.

## Using with Streamlit
We recommend the `streamlit-lottie` component for easy rendering:
- PyPI: https://pypi.org/project/streamlit-lottie/

Note: The original `streamlit-lottie` repository has been archived by the author. If you encounter
issues, you can embed Lottie via `st.components.v1.html` using Lottie Web.

## OpenWeather icon codes (for mapping ideas)
The OpenWeather docs list codes and day/night variants. You can map those to your chosen animations.
- https://openweathermap.org/weather-conditions

## How to use this pack
1. Choose animations for each condition; download `.json` files.
2. Put them in `assets/lottie/` and match names to `mapping_example.json` keys.
3. (Optional) Edit `download_lotties.py` with URLs and run it to auto-download.

## Example filenames (you will download/provide these):
- `clear-day.json`, `clear-night.json`
- `clouds.json`
- `rain.json` (also used for drizzle)
- `thunder.json`
- `snow.json`
- `mist.json`

## Disclaimer
This starter pack does not include any third-party animation assets; you must supply your own downloads.
