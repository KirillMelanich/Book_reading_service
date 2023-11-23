from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Book, ReadingSession, Profile
from .serializers import (
    BookSerializer,
    ReadingSessionSerializer,
    BookDetailSerializer,
    ProfileSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer


class ReadingSessionViewSet(viewsets.ModelViewSet):
    queryset = ReadingSession.objects.all()
    serializer_class = ReadingSessionSerializer

    def perform_create(self, serializer):
        # Set the 'user' field based on the logged-in user
        serializer.save(user=self.request.user)

        # Update the number_of_reading_sessions and last_activity in the associated Profile
        profile = self.request.user.profile
        profile.update_reading_sessions_count()
        profile.last_activity = serializer.instance.start_time
        profile.save()

    def create(self, request, *args, **kwargs):
        # Check if the user already has an active session and stop it
        active_sessions = ReadingSession.objects.filter(
            user=request.user, end_time=None
        )
        if active_sessions.exists():
            active_sessions.first().stop_reading()

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def stop_reading(self, request, pk=None):
        reading_session = self.get_object()
        reading_session.end_time = timezone.now()
        reading_session.save()

        # Update the number_of_reading_sessions in the associated Profile
        reading_session.user.profile.update_reading_sessions_count()

        serializer = ReadingSessionSerializer(reading_session)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
