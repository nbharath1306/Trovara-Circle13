from django.db import models


class ResearchTask(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("searching", "Searching Web"),
        ("reading", "Reading Sources"),
        ("summarizing", "Summarizing Content"),
        ("generating", "Generating Report"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    # Core fields
    topic = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Agent output fields
    search_results = models.JSONField(default=list, blank=True)
    sources_text = models.JSONField(default=list, blank=True)
    summaries = models.JSONField(default=list, blank=True)
    report = models.TextField(blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.topic[:60]}"
