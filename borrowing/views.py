from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingCreateSerializer, BorrowingSerializer
from library.models import Book


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    lookup_value_regex = "[0-9]+"

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active = is_active.lower()
            if is_active in ("true", "1", "yes"):
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active in ("false", "0", "no"):
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        with transaction.atomic():
            borrowing = self.get_queryset().select_for_update().get(pk=pk)

            if borrowing.actual_return_date is not None:
                return Response(
                    {"detail": "This borrowing has already been returned."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            borrowing.actual_return_date = timezone.localdate()
            borrowing.save(update_fields=["actual_return_date"])

            Book.objects.filter(pk=borrowing.book_id).update(inventory=F("inventory") + 1)
            borrowing.book.refresh_from_db(fields=["inventory"])

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
