from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, ReadingSession
from .serializers import BookSerializer, ReadingSessionSerializer, BookDetailSerializer


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

    @action(detail=True, methods=['post'])
    def start_reading(self, request, pk=None):
        book = Book.objects.get(pk=pk)
        user = request.user
        reading_session = ReadingSession.objects.create(user=user, book=book)
        serializer = ReadingSessionSerializer(reading_session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def stop_reading(self, request, pk=None):
        reading_session = self.get_object()
        reading_session.end_time = timezone.now()
        reading_session.save()
        serializer = ReadingSessionSerializer(reading_session)
        return Response(serializer.data)
