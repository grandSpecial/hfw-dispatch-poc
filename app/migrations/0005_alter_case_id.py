# Generated by Django 5.0 on 2023-12-27 12:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="id",
            field=models.CharField(
                editable=False, max_length=5, primary_key=True, serialize=False
            ),
        ),
    ]
