from django.contrib import admin
from .models import Novel, Chapter, Rating, Wishlist, ReadingHistory, WriterRequest


@admin.register(WriterRequest)
class WriterRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'reason')


admin.site.register(Novel)
admin.site.register(Chapter)
admin.site.register(Rating)
admin.site.register(Wishlist)
admin.site.register(ReadingHistory)
