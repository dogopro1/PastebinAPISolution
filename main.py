import os
import re
import requests
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
print("DEBUG: SERPAPI_KEY =", SERPAPI_KEY)

@app.get("/")
def root():
    return {
        "message": "Pastebin Search API",
        "usage": "Use /search?q=your_search_term to search Pastebin",
        "docs": "Visit /docs for interactive API documentation"
    }

def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%b %d, %Y")
    except:
        return datetime.min  # Fallback dla błędnych/nieznanych dat

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    if not SERPAPI_KEY:
        return JSONResponse(
            status_code=500,
            content={"error": "Brak klucza API SerpAPI. Ustaw zmienną środowiskową SERPAPI_KEY."}
        )

    search_url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"site:pastebin.com {q}",
        "api_key": SERPAPI_KEY
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Błąd podczas zapytania do SerpAPI: {str(e)}"}
        )

    results = []
    for result in data.get("organic_results", []):
        link = result.get("link")
        snippet = result.get("snippet", "")
        date = result.get("date", "unknown")

        if q.lower() in snippet.lower():
            results.append({
                "link": link,
                "snippet": snippet,
                "date": date
            })

    sorted_results = sorted(
        results,
        key=lambda x: parse_date(x.get("date", "")),
        reverse=True
    )

    return JSONResponse(content=sorted_results)
