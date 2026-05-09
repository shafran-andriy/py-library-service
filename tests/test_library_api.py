from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from library.models import Book
from library.serializers import BookSerializer
from library.views import BookViewSet
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
            inventory= -1,
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
        request = factory.post("/books/", data, format="json")
        force_authenticate(request, user=staff)

        view = BookViewSet()
        view.request = request
        response = view.create(request)

        self.assertEqual(response.status_code, 201)
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
        request = factory.put(f"/books/{book.pk}/", data, format="json")
        force_authenticate(request, user=staff)

        view = BookViewSet()
        view.request = request
        view.kwargs = {"pk": str(book.pk)}
        response = view.update(request, pk=book.pk)

        self.assertEqual(response.status_code, 200)
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
        request = factory.patch(f"/books/{book.pk}/", data, format="json")
        force_authenticate(request, user=staff)

        view = BookViewSet()
        view.request = request
        view.kwargs = {"pk": str(book.pk)}
        response = view.partial_update(request, pk=book.pk)

        self.assertEqual(response.status_code, 200)
        book.refresh_from_db()
        self.assertEqual(book.inventory, 1)

    def test_delete_book(self):
        User = get_user_model()
        staff = User.objects.create_user(email="staff4@example.com", password="pw")
        staff.is_staff = True
        staff.save()

        book = Book.objects.create(title="ToDelete", author="D", inventory=1, daily_fee=Decimal("0.99"))
        factory = APIRequestFactory()
        request = factory.delete(f"/books/{book.pk}/")
        force_authenticate(request, user=staff)

        view = BookViewSet()
        view.request = request
        view.kwargs = {"pk": str(book.pk)}
        response = view.destroy(request, pk=book.pk)

        self.assertIn(response.status_code, (204, 200))
        self.assertFalse(Book.objects.filter(pk=book.pk).exists())
