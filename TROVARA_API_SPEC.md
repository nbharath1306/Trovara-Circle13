# REST API Specification

## Base URL

- Local development: `http://localhost:8000/api/`
- Production: `https://your-app.onrender.com/api/`

## Endpoints

---

### 1. Submit a Research Topic

**POST** `/api/research/`

Creates a new ResearchTask and kicks off the Celery agent in the background.

**Request Body:**
```json
{
  "topic": "quantum computing basics"
}
```

**Response — 201 Created:**
```json
{
  "id": 1,
  "topic": "quantum computing basics",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "report": "",
  "error": ""
}
```

**Validation:**
- `topic` is required
- `topic` must be between 3 and 500 characters

---

### 2. Get Task Status + Result

**GET** `/api/research/<id>/`

Poll this endpoint to check progress. Returns current status and the report once done.

**Response — 200 OK (in progress):**
```json
{
  "id": 1,
  "topic": "quantum computing basics",
  "status": "summarizing",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:10Z",
  "search_results": [
    { "title": "What is Quantum Computing?", "url": "https://...", "snippet": "..." }
  ],
  "summaries": [],
  "report": "",
  "error": ""
}
```

**Response — 200 OK (completed):**
```json
{
  "id": 1,
  "topic": "quantum computing basics",
  "status": "done",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:45Z",
  "search_results": [ ... ],
  "summaries": [ ... ],
  "report": "# Research Report: Quantum Computing Basics\n\n## Introduction\n...",
  "error": ""
}
```

**Response — 200 OK (failed):**
```json
{
  "id": 1,
  "topic": "quantum computing basics",
  "status": "failed",
  "report": "",
  "error": "Groq API rate limit exceeded. Please try again later."
}
```

**Response — 404 Not Found:**
```json
{
  "detail": "Not found."
}
```

---

### 3. List All Research Tasks

**GET** `/api/research/`

Returns all tasks, newest first. Useful for the dashboard history view.

**Response — 200 OK:**
```json
[
  {
    "id": 3,
    "topic": "machine learning overview",
    "status": "done",
    "created_at": "2024-01-15T11:00:00Z"
  },
  {
    "id": 2,
    "topic": "blockchain technology",
    "status": "failed",
    "created_at": "2024-01-15T10:45:00Z"
  },
  {
    "id": 1,
    "topic": "quantum computing basics",
    "status": "done",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### 4. Delete a Task

**DELETE** `/api/research/<id>/`

Removes a task and its results from the database.

**Response — 204 No Content** (success, empty body)

---

## Serializers

```python
# agent/serializers.py

from rest_framework import serializers
from .models import ResearchTask

class ResearchTaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the list view."""
    class Meta:
        model = ResearchTask
        fields = ["id", "topic", "status", "created_at"]


class ResearchTaskDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all agent output fields."""
    class Meta:
        model = ResearchTask
        fields = [
            "id", "topic", "status",
            "created_at", "updated_at",
            "search_results", "summaries",
            "report", "error"
        ]
        read_only_fields = [
            "status", "created_at", "updated_at",
            "search_results", "summaries", "report", "error"
        ]
```

---

## Views

```python
# agent/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .models import ResearchTask
from .serializers import ResearchTaskListSerializer, ResearchTaskDetailSerializer
from .tasks import run_trovara

class ResearchTaskListCreateView(generics.ListCreateAPIView):
    queryset = ResearchTask.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResearchTaskDetailSerializer
        return ResearchTaskListSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        # Kick off the Celery agent
        run_trovara.delay(task.id)


class ResearchTaskDetailView(generics.RetrieveDestroyAPIView):
    queryset = ResearchTask.objects.all()
    serializer_class = ResearchTaskDetailSerializer
```

---

## URL Configuration

```python
# agent/urls.py

from django.urls import path
from .views import ResearchTaskListCreateView, ResearchTaskDetailView

urlpatterns = [
    path("research/",      ResearchTaskListCreateView.as_view(), name="research-list-create"),
    path("research/<int:pk>/", ResearchTaskDetailView.as_view(),  name="research-detail"),
]
```

```python
# trovara/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/",  admin.site.urls),
    path("api/",    include("agent.urls")),
    path("",        TemplateView.as_view(template_name="index.html"), name="home"),
]
```
