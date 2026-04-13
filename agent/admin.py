from django.contrib import admin
from .models import ResearchTask


@admin.register(ResearchTask)
class ResearchTaskAdmin(admin.ModelAdmin):
    list_display = ["topic", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["topic"]
    readonly_fields = [
        "created_at", "updated_at", "search_results",
        "sources_text", "summaries", "report", "error",
    ]
