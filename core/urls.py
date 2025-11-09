from django.urls import path
from . import views
urlpatterns = [
    path("browse/", views.browse, name="browse"),
    path("api/search", views.search, name="api_search"),
    path("api/item/<str:item_type>/<str:item_id>", views.item_detail, name="api_item"),
    path("api/recs/<str:item_type>/<str:item_id>", views.recs, name="api_recs"),
    path("api/list/toggle", views.list_toggle, name="api_list_toggle"),
    path("api/rate", views.rate, name="api_rate"),
    path("me/lists/", views.my_lists, name="my_lists"),

    # Trending content endpoints
    path("api/trending/<str:content_type>", views.trending, name="api_trending"),
    path("api/top-rated/<str:content_type>", views.top_rated, name="api_top_rated"),
    path("api/latest/<str:content_type>", views.latest, name="api_latest"),
    path("api/on-air/<str:content_type>", views.on_air, name="api_on_air"),
    path("api/new-releases/<str:content_type>", views.new_releases, name="api_new_releases"),
    path("api/featured/<str:content_type>", views.featured, name="api_featured"),
]
