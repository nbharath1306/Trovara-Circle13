from django.urls import path
from .views import ResearchTaskListCreateView, ResearchTaskDetailView

urlpatterns = [
    path("research/", ResearchTaskListCreateView.as_view(), name="research-list-create"),
    path("research/<int:pk>/", ResearchTaskDetailView.as_view(), name="research-detail"),
]
