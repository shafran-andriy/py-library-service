from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from library.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        ordering = ["-borrow_date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(expected_return_date__gt=F("borrow_date")),
                name="expected_return_after_borrow",
            ),
            models.CheckConstraint(
                condition=Q(actual_return_date__isnull=True)
                | Q(actual_return_date__gte=F("borrow_date")),
                name="actual_return_not_before_borrow",
            ),
        ]

    @property
    def is_active(self):
        return self.actual_return_date is None

    def clean(self):
        if self.expected_return_date <= self.borrow_date:
            raise ValidationError(
                {"expected_return_date": "Expected return date must be after borrow date."}
            )

        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError(
                {"actual_return_date": "Actual return date cannot be before borrow date."}
            )

    def __str__(self):
        return f"{self.book} borrowed by {self.user}"
