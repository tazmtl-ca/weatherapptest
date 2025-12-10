
"""Download Lottie JSON animations into assets/lottie/ based on a mapping file."""
import os, json, requests

ROOT = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(ROOT, "assets", "lottie")
MAPPING_FILE = os.path.join(ROOT, "mapping_example.json")

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    for key, item in mapping.items():
        url = item.get("url")
        filename = item.get("filename")
        if not url:
            print(f"[skip] {key}: no URL provided")
            continue
        outpath = os.path.join(ASSETS_DIR, filename)
        print(f"[download] {key}: {url} -> {outpath}")
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"  [error] failed to fetch {url}: {e}")
            continue
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"  [ok] saved {outpath}")

if __name__ == "__main__":
    main()
