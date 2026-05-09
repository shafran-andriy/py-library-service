from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request as DRFRequest
from django.utils import timezone
from datetime import timedelta
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingCreateSerializer
from borrowing.views import BorrowingViewSet
from library.models import Book
from django.contrib.auth import get_user_model


class BorrowingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email="u@example.com", password="pass")
        self.factory = APIRequestFactory()

    def test_create_borrowing_decrements_inventory(self):
        book = Book.objects.create(title="B1", author="A1", inventory=2, daily_fee=1.00)
        expected_return = timezone.localdate() + timedelta(days=2)
        data = {"book": book.pk, "expected_return_date": expected_return}
        raw = self.factory.post("/borrowings/", data, format='json')
        drf_req = DRFRequest(raw)
        drf_req.user = self.user
        serializer = BorrowingCreateSerializer(data=data, context={"request": drf_req})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        borrowing = serializer.save()
        book.refresh_from_db()
        self.assertEqual(book.inventory, 1)
        self.assertEqual(borrowing.user, self.user)

    def test_validate_book_unavailable(self):
        book = Book.objects.create(title="B2", author="A2", inventory=0, daily_fee=1.00)
        expected_return = timezone.localdate() + timedelta(days=2)
        data = {"book": book.pk, "expected_return_date": expected_return}
        raw = self.factory.post("/borrowings/", data, format='json')
        drf_req = DRFRequest(raw)
        drf_req.user = self.user
        serializer = BorrowingCreateSerializer(data=data, context={"request": drf_req})
        self.assertFalse(serializer.is_valid())
        self.assertIn('book', serializer.errors)

    def test_return_borrowing_action_increments_inventory(self):
        book = Book.objects.create(title="B3", author="A3", inventory=1, daily_fee=1.00)
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timedelta(days=1),
            book=book,
            user=self.user,
        )
        raw = self.factory.post(f"/borrowings/{borrowing.pk}/return/")
        drf_req = DRFRequest(raw)
        drf_req.user = self.user
        view = BorrowingViewSet()
        view.request = drf_req
        view.kwargs = {"pk": str(borrowing.pk)}
        view.args = ()
        view.format_kwarg = None
        view.action = 'return'
        response = view.return_borrowing(drf_req, pk=borrowing.pk)
        book.refresh_from_db()
        borrowing.refresh_from_db()
        self.assertEqual(book.inventory, 2)
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(response.status_code, 200)
