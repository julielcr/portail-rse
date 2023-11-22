# Generated by Django 4.2.6 on 2023-11-15 10:08
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        (
            "entreprises",
            "0036_caracteristiquesannuelles_effectif_groupe_permanent_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="entreprise",
            name="est_cotee",
            field=models.BooleanField(
                null=True,
                verbose_name="L'entreprise est cotée sur un marché réglementé européen",
            ),
        ),
    ]
