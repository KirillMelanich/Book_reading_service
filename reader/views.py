from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, ReadingSession
from .serializers import BookSerializer, ReadingSessionSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class ReadingSessionViewSet(viewsets.ModelViewSet):
    queryset = ReadingSession.objects.all()
    serializer_class = ReadingSessionSerializer

    @action(detail=True, methods=['post'])
    def start_reading_session(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(data={'book': book.id, 'start_time': timezone.now()})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'])
    def end_reading_session(self, request, pk=None):
        session = self.get_object()
        session.end_time = timezone.now()
        session.save()
        serializer = self.get_serializer(session)
        return Response(serializer.data)
