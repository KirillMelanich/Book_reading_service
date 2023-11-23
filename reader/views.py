from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response


from .models import Book, ReadingSession, Profile
from .permissions import IsAdminOrIfAuthentificatedReadOnly, IsOwnerOrReadOnly
from .serializers import (
    BookSerializer,
    ReadingSessionSerializer,
    BookDetailSerializer,
    ProfileSerializer,
)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthentificatedReadOnly, )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer


class ReadingSessionViewSet(viewsets.ModelViewSet):
    queryset = ReadingSession.objects.all()
    serializer_class = ReadingSessionSerializer
    pagination_class = Pagination
    permission_classes = (IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        # Set the 'user' field based on the logged-in user
        serializer.save(user=self.request.user)

        # Update the number_of_reading_sessions and last_activity in the associated Profile
        profile = self.request.user.profile
        profile.update_reading_sessions_count()
        profile.calculate_total_reading_time_for_user()
        profile.get_last_book_read()
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

        # Check if the reading session has already been completed
        if reading_session.end_time:
            return Response(
                {"detail": "Reading session has already been completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reading_session.end_time = timezone.now()
        reading_session.save()

        # Update the number_of_reading_sessions in the associated Profile
        reading_session.user.profile.update_reading_sessions_count()

        serializer = ReadingSessionSerializer(reading_session)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrReadOnly, )
