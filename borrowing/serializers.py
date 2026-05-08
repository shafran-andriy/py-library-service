from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from borrowing.models import Borrowing
from library.models import Book
from library.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    borrow_date = serializers.DateField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("actual_return_date",)

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("This book is not available now.")
        return book

    def validate(self, attrs):
        borrow_date = timezone.localdate()
        expected_return_date = attrs["expected_return_date"]

        if expected_return_date <= borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return_date": (
                        "Expected return date must be after borrow date."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        book = validated_data.pop("book")

        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book.pk)
            if book.inventory == 0:
                raise serializers.ValidationError(
                    {"book": "This book is not available now."}
                )

            borrowing = Borrowing.objects.create(
                **validated_data,
                borrow_date=timezone.localdate(),
                user=request.user,
                book=book,
            )
            book.inventory -= 1
            book.save(update_fields=["inventory"])

        return borrowing
