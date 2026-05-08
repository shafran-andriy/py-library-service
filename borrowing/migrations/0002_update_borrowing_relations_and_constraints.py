# Generated manually to preserve existing borrowing rows while moving to FK fields.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):

    dependencies = [
        ("borrowing", "0001_initial"),
        ("library", "0002_delete_borrowing"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="borrowing",
            old_name="expected_return",
            new_name="expected_return_date",
        ),
        migrations.RenameField(
            model_name="borrowing",
            old_name="actual_return",
            new_name="actual_return_date",
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name="borrowing",
            old_name="book_id",
            new_name="book",
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="book",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to="library.book",
            ),
        ),
        migrations.RenameField(
            model_name="borrowing",
            old_name="user_id",
            new_name="user",
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name="borrowing",
            options={"ordering": ["-borrow_date", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                condition=Q(("expected_return_date__gt", F("borrow_date"))),
                name="expected_return_after_borrow",
            ),
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                condition=(
                    Q(("actual_return_date__isnull", True))
                    | Q(("actual_return_date__gte", F("borrow_date")))
                ),
                name="actual_return_not_before_borrow",
            ),
        ),
    ]
