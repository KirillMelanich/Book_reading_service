# Generated by Django 4.2.7 on 2023-12-06 12:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0002_alter_book_author_alter_book_long_description_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["id"]},
        ),
        migrations.AlterModelOptions(
            name="readingsession",
            options={"ordering": ["id"]},
        ),
    ]