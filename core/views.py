from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.contrib.auth.forms import UserCreationForm

from .models import UserList, Review
from .services import (
    tmdb_search, rawg_search, spotify_search,
    tmdb_item, rawg_item, spotify_album,
    tmdb_recs, rawg_recs, spotify_recs,
    tmdb_tv_item, tmdb_tv_recs,
    # Trending functions
    tmdb_trending_movies, tmdb_trending_tv, tmdb_top_rated_movies, tmdb_top_rated_tv,
    tmdb_latest_movies, tmdb_on_air_tv, rawg_trending_games, rawg_top_rated_games,
    rawg_new_games, spotify_trending_albums, spotify_new_releases, spotify_featured_artists
)

# ---------- Basic pages ----------

def home(request):
    return render(request, "home.html")

def browse(request):
    return render(request, "browse.html")

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# ---------- Public JSON APIs ----------

@require_http_methods(["GET"])
def search(request):
    q = request.GET.get("q", "").strip()
    item_type = request.GET.get("type", "all")
    if not q:
        return JsonResponse({"results": []})

    results = []
    if item_type in ("all", "movie", "tv"):   # tmdb_search now emits movie or tv
        results += tmdb_search(q)
    if item_type in ("all", "game"):
        results += rawg_search(q)
    if item_type in ("all", "album"):
        results += spotify_search(q)
    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def item_detail(request, item_type, item_id):
    if item_type == "movie":
        data = tmdb_item(item_id)
    elif item_type == "tv":
        data = tmdb_tv_item(item_id)
    elif item_type == "game":
        data = rawg_item(item_id)
    elif item_type == "album":
        data = spotify_album(item_id)
    else:
        return HttpResponseBadRequest("unknown type")

    agg = Review.objects.filter(item_type=item_type, item_id=item_id)\
                        .aggregate(avg=Avg("rating"), n=Count("id"))
    return JsonResponse({"provider_payload": data, "local_rating": agg})

@require_http_methods(["GET"])
def recs(request, item_type, item_id):
    if item_type == "movie":
        items = tmdb_recs(item_id)
    elif item_type == "tv":
        items = tmdb_tv_recs(item_id)
    elif item_type == "game":
        items = rawg_recs(item_id)
    elif item_type == "album":
        items = spotify_recs(item_id)
    else:
        return HttpResponseBadRequest("unknown type")
    return JsonResponse({"results": items})

# ---------- Auth-required JSON APIs ----------

@login_required
@require_http_methods(["POST"])
def list_toggle(request):
    item_id = request.POST.get("item_id")
    item_type = request.POST.get("item_type")
    list_type = request.POST.get("list_type")

    obj, created = UserList.objects.get_or_create(
        user=request.user,
        item_type=item_type,
        item_id=item_id,
        list_type=list_type
    )
    if not created:
        obj.delete()

    count = UserList.objects.filter(user=request.user, list_type=list_type).count()
    return JsonResponse({"in_list": created, "count": count})

@login_required
@require_http_methods(["POST"])
def rate(request):
    item_id = request.POST.get("item_id")
    item_type = request.POST.get("item_type")
    rating = int(request.POST.get("rating", "0"))
    text = request.POST.get("text", "")

    Review.objects.update_or_create(
        user=request.user,
        item_type=item_type,
        item_id=item_id,
        defaults={"rating": rating, "text": text}
    )

    agg = Review.objects.filter(item_type=item_type, item_id=item_id)\
                        .aggregate(avg=Avg("rating"), n=Count("id"))
    return JsonResponse({"ok": True, "local_rating": agg})

# ---------- Lists page (HTML) ----------

@login_required
def my_lists(request):
    rows = UserList.objects.filter(user=request.user).order_by('-created_at')
    grouped = {'watch': [], 'play': [], 'listen': []}

    for r in rows:
        title = cover = year = ""
        try:
            if r.item_type == "movie":
                data = tmdb_item(r.item_id)
                title = data.get("title") or data.get("name") or ""
                year  = (data.get("release_date") or "")[:4]
                pp = data.get("poster_path")
                cover = f"https://image.tmdb.org/t/p/w500{pp}" if pp else ""
            elif r.item_type == "tv":
                data = tmdb_tv_item(r.item_id)
                title = data.get("name", "")
                year  = (data.get("first_air_date") or "")[:4]
                pp = data.get("poster_path")
                cover = f"https://image.tmdb.org/t/p/w500{pp}" if pp else ""
            elif r.item_type == "game":
                data = rawg_item(r.item_id)
                title = data.get("name", "")
                year  = (data.get("released") or "")[:4]
                cover = data.get("background_image", "")
            elif r.item_type == "album":
                data = spotify_album(r.item_id)
                title = data.get("name", "")
                year  = (data.get("release_date") or "")[:4]
                images = data.get("images") or []
                cover = images[0]["url"] if images else ""
            else:
                continue

            grouped[r.list_type].append({
                "type": r.item_type,
                "id": r.item_id,
                "title": title,
                "year": year,
                "cover": cover
            })
        except Exception:
            # Skip any items that 404/fail from providers
            continue

    return render(request, "lists.html", {"grouped": grouped})

# ---------- Trending Content APIs ----------

@require_http_methods(["GET"])
def trending(request, content_type):
    """Get trending content by type"""
    if content_type == "movies":
        results = tmdb_trending_movies()
    elif content_type == "tv":
        results = tmdb_trending_tv()
    elif content_type == "music":
        results = spotify_trending_albums()
    elif content_type == "games":
        results = rawg_trending_games()
    else:
        return HttpResponseBadRequest("Invalid content type")

    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def top_rated(request, content_type):
    """Get top rated content by type"""
    if content_type == "movies":
        results = tmdb_top_rated_movies()
    elif content_type == "tv":
        results = tmdb_top_rated_tv()
    elif content_type == "music":
        results = spotify_trending_albums()  # Use trending as fallback
    elif content_type == "games":
        results = rawg_top_rated_games()
    else:
        return HttpResponseBadRequest("Invalid content type")

    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def latest(request, content_type):
    """Get latest content by type"""
    if content_type == "movies":
        results = tmdb_latest_movies()
    elif content_type == "tv":
        results = tmdb_on_air_tv()
    elif content_type == "music":
        results = spotify_new_releases()
    elif content_type == "games":
        results = rawg_new_games()
    else:
        return HttpResponseBadRequest("Invalid content type")

    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def on_air(request, content_type):
    """Get on air TV shows"""
    if content_type == "tv":
        results = tmdb_on_air_tv()
    else:
        return HttpResponseBadRequest("Only TV shows supported")

    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def new_releases(request, content_type):
    """Get new releases by type"""
    if content_type == "music":
        results = spotify_new_releases()
    elif content_type == "games":
        results = rawg_new_games()
    else:
        return HttpResponseBadRequest("Invalid content type")

    return JsonResponse({"results": results})

@require_http_methods(["GET"])
def featured(request, content_type):
    """Get featured content by type"""
    if content_type == "music":
        results = spotify_featured_artists()
    else:
        return HttpResponseBadRequest("Only music supported")

    return JsonResponse({"results": results})
