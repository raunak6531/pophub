from django.contrib import admin
from .models import Review, UserList, CachedResponse

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user','item_type','item_id','rating','created_at')
    search_fields = ('item_id','user__username')
    list_filter = ('item_type','rating')

@admin.register(UserList)
class UserListAdmin(admin.ModelAdmin):
    list_display = ('user','list_type','item_type','item_id','created_at')
    search_fields = ('item_id','user__username')
    list_filter = ('list_type','item_type')

@admin.register(CachedResponse)
class CachedResponseAdmin(admin.ModelAdmin):
    list_display = ('url','created_at')
    search_fields = ('url',)
