import requests

def search_music_itunes(query, limit=5):
    url = f"https://itunes.apple.com/search?term={query}&media=music&limit={limit}"
    response = requests.get(url)
    data = response.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item["trackName"],
            "artist": item["artistName"],
            "preview_url": item.get("previewUrl", "No preview available")
        })
    return results