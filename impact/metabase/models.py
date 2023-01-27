from utils.models import TimestampedModel
from django.db import models
from entreprises.models import RAISON_SOCIALE_MAX_LENGTH


class Entreprise(TimestampedModel):
    siren = models.CharField(max_length=9, unique=True)
    effectif = models.CharField(max_length=9)
    bdese_accord = models.BooleanField(default=False)
    raison_sociale = models.CharField(max_length=RAISON_SOCIALE_MAX_LENGTH)

    def __str__(self):
        return f"{self.siren} {self.raison_sociale}"
