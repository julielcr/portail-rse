# Generated by Django 4.1.7 on 2023-03-15 15:35
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("entreprises", "0012_delete_habilitation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entreprise",
            name="bdese_accord",
            field=models.BooleanField(
                default=False,
                verbose_name="L'entreprise a un accord collectif d'entreprise concernant la Base de Données Économiques, Sociales et Environnementales (BDESE)",
            ),
        ),
    ]
