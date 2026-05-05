from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from library.models import Book, Borrowing
from library.permissions import IsAdminOrIfAuthenticatedReadOnly
from library.serializers import BookSerializer, BorrowingSerializer


class BookViewSet(mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class BorrowingViewSet(mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
