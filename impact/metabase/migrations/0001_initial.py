# Generated by Django 4.1.5 on 2023-01-27 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entreprise",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("siren", models.CharField(max_length=9, unique=True)),
                ("effectif", models.CharField(max_length=9)),
                ("bdese_accord", models.BooleanField(default=False)),
                ("raison_sociale", models.CharField(max_length=250)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
