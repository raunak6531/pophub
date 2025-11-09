import base64, time, requests
from django.utils import timezone
from django.conf import settings
from .models import CachedResponse

def tmdb_search(q):
    ...
    for r in data.get("results", []):
        mt = r.get("media_type")  # "movie" or "tv"
        if mt not in ("movie", "tv"):
            continue
        out.append({
            "type": "tv" if mt == "tv" else "movie",   # <-- was always "movie"
            "id": str(r["id"]),
            "title": r.get("title") or r.get("name"),
            "year": (r.get("release_date") or r.get("first_air_date") or "")[:4],
            "genres": [],
            "cover": f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get("poster_path") else "",
            "summary": r.get("overview",""),
            "provider":"tmdb"
        })

def tmdb_tv_item(tv_id):
    url = f"{TMDB_BASE}/tv/{tv_id}?api_key={settings.TMDB_API_KEY}&append_to_response=videos,similar"
    return fetch_with_cache(url)

def tmdb_tv_recs(tv_id):
    data = tmdb_tv_item(tv_id)
    sims = data.get("similar",{}).get("results",[])
    return [{"type":"tv","id":str(x["id"]),"title":x.get("name"),
             "cover": f"https://image.tmdb.org/t/p/w500{x['poster_path']}" if x.get("poster_path") else ""} 
            for x in sims]

def fetch_with_cache(url, headers=None):
    rec = CachedResponse.objects.filter(url=url).first()
    if rec and rec.is_fresh:
        return rec.payload
    resp = requests.get(url, headers=headers or {}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if rec:
        rec.payload = data; rec.created_at = timezone.now(); rec.save()
    else:
        CachedResponse.objects.create(url=url, payload=data)
    return data

# ---------- TMDB ----------
TMDB_BASE = "https://api.themoviedb.org/3"
def tmdb_search(q):
    if not settings.TMDB_API_KEY:
        return []
    from requests.utils import quote
    url = f"{TMDB_BASE}/search/multi?api_key={settings.TMDB_API_KEY}&query={quote(q)}"
    data = fetch_with_cache(url)
    out = []
    for r in data.get("results", []):
        mt = r.get("media_type")
        if mt not in ("movie", "tv"):
            continue

        out.append({
            "type": "tv" if mt == "tv" else "movie",   # ✅ THIS IS THE FIX
            "id": str(r["id"]),
            "title": r.get("title") or r.get("name"),
            "year": (r.get("release_date") or r.get("first_air_date") or "")[:4],
            "genres": [],
            "cover": f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get("poster_path") else "",
            "summary": r.get("overview",""),
            "provider":"tmdb"
        })
    return out


def tmdb_item(movie_id):
    url = f"{TMDB_BASE}/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&append_to_response=videos,similar"
    return fetch_with_cache(url)

def tmdb_recs(movie_id):
    data = tmdb_item(movie_id)
    sims = data.get("similar",{}).get("results",[])
    return [{"type":"movie","id":str(x["id"]),"title":x.get("title"),
             "cover": f"https://image.tmdb.org/t/p/w500{x['poster_path']}" if x.get("poster_path") else ""}
            for x in sims]

# ---------- RAWG ----------
RAWG_BASE = "https://api.rawg.io/api"
def rawg_search(q):
    if not settings.RAWG_API_KEY:
        return []
    from requests.utils import quote
    url = f"{RAWG_BASE}/games?key={settings.RAWG_API_KEY}&search={quote(q)}"
    data = fetch_with_cache(url)
    out = []
    for r in data.get("results", []):
        out.append({
            "type":"game",
            "id": str(r["id"]),
            "title": r["name"],
            "year": (r.get("released") or "")[:4],
            "genres": [g["name"] for g in r.get("genres",[])],
            "platforms": [p["platform"]["name"] for p in r.get("platforms",[]) if p.get("platform")],
            "cover": r.get("background_image",""),
            "summary": "",
            "provider":"rawg"
        })
    return out

def rawg_item(game_id):
    url = f"{RAWG_BASE}/games/{game_id}?key={settings.RAWG_API_KEY}"
    return fetch_with_cache(url)

def rawg_recs(game_id):
    url = f"{RAWG_BASE}/games/{game_id}/suggested?key={settings.RAWG_API_KEY}"
    data = fetch_with_cache(url)
    if data.get("results"):
        return [{"type":"game","id":str(x["id"]),"title":x["name"],"cover":x.get("background_image","")} for x in data["results"]]
    g = rawg_item(game_id)
    if g.get("genres"):
        genre = g["genres"][0]["slug"]
        url2 = f"{RAWG_BASE}/games?key={settings.RAWG_API_KEY}&genres={genre}&ordering=-rating&page_size=10"
        data2 = fetch_with_cache(url2)
        return [{"type":"game","id":str(x["id"]),"title":x["name"],"cover":x.get("background_image","")} for x in data2.get("results",[])]
    return []

# ---------- Spotify ----------
_spotify_token = {"value": None, "exp": 0}
def spotify_token():
    import base64, time, requests
    if time.time() < _spotify_token["exp"] - 30:
        return _spotify_token["value"]
    creds = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    headers = {"Authorization":"Basic "+base64.b64encode(creds).decode(),
               "Content-Type":"application/x-www-form-urlencoded"}
    resp = requests.post("https://accounts.spotify.com/api/token",
        headers=headers, data={"grant_type":"client_credentials"}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    _spotify_token["value"] = data["access_token"]
    _spotify_token["exp"] = time.time() + data["expires_in"]
    return _spotify_token["value"]

def spotify_search(q):
    if not (settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET):
        return []
    tok = spotify_token()
    headers = {"Authorization": f"Bearer {tok}"}
    from requests.utils import quote
    url = f"https://api.spotify.com/v1/search?type=album&q={quote(q)}&limit=10"
    data = fetch_with_cache(url, headers=headers)
    out = []
    for a in data.get("albums",{}).get("items",[]):
        out.append({
            "type":"album",
            "id": a["id"],
            "title": a["name"],
            "year": (a.get("release_date") or "")[:4],
            "genres": [],
            "creators": ", ".join([ar["name"] for ar in a.get("artists",[])]),
            "cover": a.get("images",[{"url":""}])[0]["url"] if a.get("images") else "",
            "summary": "",
            "provider":"spotify"
        })
    return out

def spotify_album(album_id):
    tok = spotify_token()
    headers = {"Authorization": f"Bearer {tok}"}
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    return fetch_with_cache(url, headers=headers)

def spotify_recs(album_id):
    a = spotify_album(album_id)
    if a.get("artists"):
        artist_id = a["artists"][0]["id"]
        tok = spotify_token()
        headers = {"Authorization": f"Bearer {tok}"}
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&limit=10"
        data = fetch_with_cache(url, headers=headers)
        return [{"type":"album","id":x["id"],"title":x["name"],
                 "cover":(x.get("images",[{"url":""}])[0]["url"] if x.get("images") else "")}
                for x in data.get("items",[])]
    return []

# ---------- TRENDING CONTENT FUNCTIONS ----------

def tmdb_trending_movies():
    """Get trending movies from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "movie")

def tmdb_trending_tv():
    """Get trending TV shows from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/trending/tv/week?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "tv")

def tmdb_top_rated_movies():
    """Get top rated movies from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/movie/top_rated?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "movie")

def tmdb_top_rated_tv():
    """Get top rated TV shows from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/tv/top_rated?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "tv")

def tmdb_latest_movies():
    """Get latest movies from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/movie/now_playing?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "movie")

def tmdb_on_air_tv():
    """Get TV shows on air today from TMDB"""
    if not settings.TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/tv/on_the_air?api_key={settings.TMDB_API_KEY}"
    data = fetch_with_cache(url)
    return format_tmdb_results(data.get("results", []), "tv")

def format_tmdb_results(results, content_type):
    """Format TMDB results into consistent format"""
    formatted = []
    for r in results:
        formatted.append({
            "type": content_type,
            "id": str(r["id"]),
            "title": r.get("title") or r.get("name"),
            "year": (r.get("release_date") or r.get("first_air_date") or "")[:4],
            "genres": [g["name"] for g in r.get("genres", [])] if "genres" in r else [],
            "cover": f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get("poster_path") else "",
            "overview": r.get("overview", ""),
            "rating": r.get("vote_average", 0),
            "provider": "tmdb"
        })
    return formatted

def rawg_trending_games():
    """Get trending games from RAWG"""
    if not settings.RAWG_API_KEY:
        return []
    url = f"{RAWG_BASE}/games?key={settings.RAWG_API_KEY}&dates=2023-01-01,2024-12-31&ordering=-added"
    data = fetch_with_cache(url)
    return format_rawg_results(data.get("results", []))

def rawg_top_rated_games():
    """Get top rated games from RAWG"""
    if not settings.RAWG_API_KEY:
        return []
    url = f"{RAWG_BASE}/games?key={settings.RAWG_API_KEY}&ordering=-rating"
    data = fetch_with_cache(url)
    return format_rawg_results(data.get("results", []))

def rawg_new_games():
    """Get new games from RAWG"""
    if not settings.RAWG_API_KEY:
        return []
    url = f"{RAWG_BASE}/games?key={settings.RAWG_API_KEY}&dates=2024-01-01,2024-12-31&ordering=-released"
    data = fetch_with_cache(url)
    return format_rawg_results(data.get("results", []))

def format_rawg_results(results):
    """Format RAWG results into consistent format"""
    formatted = []
    for r in results:
        formatted.append({
            "type": "game",
            "id": str(r["id"]),
            "title": r.get("name", ""),
            "year": r.get("released", "")[:4] if r.get("released") else "",
            "genres": [g["name"] for g in r.get("genres", [])],
            "cover": r.get("background_image", ""),
            "overview": r.get("description_raw", "")[:200] + "..." if r.get("description_raw") else "",
            "rating": r.get("rating", 0),
            "provider": "rawg"
        })
    return formatted

def spotify_trending_albums():
    """Get trending albums - using popular artists"""
    popular_artists = ["Taylor Swift", "Drake", "Bad Bunny", "The Weeknd", "Ariana Grande"]
    results = []
    for artist in popular_artists[:3]:
        albums = spotify_search(artist)
        results.extend(albums[:2])
    return results

def spotify_new_releases():
    """Get new music releases"""
    recent_artists = ["Sabrina Carpenter", "Chappell Roan", "Benson Boone", "Tate McRae"]
    results = []
    for artist in recent_artists[:3]:
        albums = spotify_search(artist)
        results.extend(albums[:2])
    return results

def spotify_featured_artists():
    """Get featured artists albums"""
    featured_artists = ["Billie Eilish", "Dua Lipa", "Post Malone", "Olivia Rodrigo"]
    results = []
    for artist in featured_artists[:3]:
        albums = spotify_search(artist)
        results.extend(albums[:2])
    return results
