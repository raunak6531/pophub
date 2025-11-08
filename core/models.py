from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)  # movie|album|game
    item_id = models.CharField(max_length=100)   # provider id (tmdb/spotify/rawg)
    rating = models.IntegerField()               # 1..5
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserList(models.Model):
    LIST_TYPES = [('watch','Watchlist'),('play','Backlog'),('listen','Playlist')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list_type = models.CharField(max_length=10, choices=LIST_TYPES)
    item_type = models.CharField(max_length=10)
    item_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class CachedResponse(models.Model):
    url = models.TextField(unique=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_fresh(self):
        from django.conf import settings
        return (timezone.now() - self.created_at).total_seconds() < settings.CACHE_TTL_SECONDS
