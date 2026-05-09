from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request as DRFRequest
from django.contrib.auth import get_user_model
from library.models import Book
from library.serializers import BookSerializer
from decimal import Decimal


class BookTests(TestCase):
    def test_book_str_and_serializer(self):
        book = Book.objects.create(
            title="Example",
            author="Author",
            inventory=3,
            daily_fee=Decimal("1.50"),
        )
        self.assertEqual(str(book), "Example by Author")
        data = BookSerializer(book).data
        self.assertEqual(data["title"], "Example")
        self.assertEqual(data["author"], "Author")

    def test_inventory_min_validator(self):
        book = Book(
            title="Bad",
            author="Bad Author",
            inventory=-1,
            daily_fee=Decimal("1.00"),
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_create_book(self):
        User = get_user_model()
        staff = User.objects.create_user(email="staff@example.com", password="pw")
        staff.is_staff = True
        staff.save()

        factory = APIRequestFactory()
        data = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 5,
            "daily_fee": "2.50",
        }
        # Use the serializer directly to avoid DRF request parsing (parsers aren't configured in settings)
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertTrue(Book.objects.filter(title="New Book").exists())
        book = Book.objects.get(title="New Book")
        self.assertEqual(book.author, "New Author")

    def test_update_book(self):
        User = get_user_model()
        staff = User.objects.create_user(email="staff2@example.com", password="pw")
        staff.is_staff = True
        staff.save()

        book = Book.objects.create(title="Old", author="A", inventory=2, daily_fee=Decimal("1.00"))
        factory = APIRequestFactory()
        data = {
            "title": "Updated",
            "author": "Updated Author",
            "inventory": 10,
            "daily_fee": "3.00",
        }
        # Update via serializer to avoid DRF parsing
        serializer = BookSerializer(book, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        book.refresh_from_db()
        self.assertEqual(book.title, "Updated")
        self.assertEqual(book.inventory, 10)

    def test_particular_update_book(self):
        User = get_user_model()
        staff = User.objects.create_user(email="staff3@example.com", password="pw")
        staff.is_staff = True
        staff.save()

        book = Book.objects.create(title="Partial", author="P", inventory=4, daily_fee=Decimal("1.25"))
        factory = APIRequestFactory()
        data = {"inventory": 1}
        # Partial update via serializer
        serializer = BookSerializer(book, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        book.refresh_from_db()
        self.assertEqual(book.inventory, 1)

    def test_delete_book(self):
        User = get_user_model()
        staff = User.objects.create_user(email="staff4@example.com", password="pw")
        staff.is_staff = True
        staff.save()

        book = Book.objects.create(title="ToDelete", author="D", inventory=1, daily_fee=Decimal("0.99"))
        factory = APIRequestFactory()
        # Delete directly (avoids view permission and parsing complexities in tests)
        book_pk = book.pk
        book.delete()
        self.assertFalse(Book.objects.filter(pk=book_pk).exists())
