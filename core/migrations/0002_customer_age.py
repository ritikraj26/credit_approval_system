# Generated by Django 5.0.1 on 2024-01-31 22:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="age",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]