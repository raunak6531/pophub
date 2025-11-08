from django.urls import path
from . import views
urlpatterns = [
    path("api/search", views.search, name="api_search"),
    path("api/item/<str:item_type>/<str:item_id>", views.item_detail, name="api_item"),
    path("api/recs/<str:item_type>/<str:item_id>", views.recs, name="api_recs"),
    path("api/list/toggle", views.list_toggle, name="api_list_toggle"),
    path("api/rate", views.rate, name="api_rate"),
    path("me/lists/", views.my_lists, name="my_lists"),
]
