from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
import re

app = FastAPI()

SERPAPI_KEY = "4e24077e22cbc98acce5c745afefbbf492a4ccab07e3d9f204877d3a5de99c9a"

@app.get("/")
def root():
    return {
        "message": "Pastebin Search API", 
        "usage": "Use /search?q=your_search_term to search Pastebin",
        "docs": "Visit /docs for interactive API documentation"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    search_url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"site:pastebin.com {q}",
        "api_key": SERPAPI_KEY
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    results = []
    for result in data.get("organic_results", []):
        link = result.get("link")
        snippet = result.get("snippet", "")

        try:
            paste_text = requests.get(link, timeout=5).text
            match = re.search(r".{0,30}" + re.escape(q) + r".{0,30}", paste_text, re.IGNORECASE)
            if match:
                results.append({
                    "link": link,
                    "snippet": match.group(),
                    "date": result.get("date", "unknown")
                })
        except:
            continue

    return JSONResponse(content=sorted(results, key=lambda x: x["date"], reverse=True))
