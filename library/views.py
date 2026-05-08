from rest_framework.viewsets import ModelViewSet

from library.models import Book
from library.permissions import IsAdminOrIfAuthenticatedReadOnly
from library.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
