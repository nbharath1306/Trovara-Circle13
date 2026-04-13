from rest_framework import generics
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
        run_trovara.delay(task.id)


class ResearchTaskDetailView(generics.RetrieveDestroyAPIView):
    queryset = ResearchTask.objects.all()
    serializer_class = ResearchTaskDetailSerializer
