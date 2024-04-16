from datetime import date

import requests
import sentry_sdk

from .exceptions import APIError
from .exceptions import ServerError
from .exceptions import SirenError
from .exceptions import TooManyRequestError
from entreprises.models import CaracteristiquesAnnuelles
from impact.settings import API_SIRENE_TOKEN

RECHERCHE_ENTREPRISE_TIMEOUT = 10
SIREN_NOT_FOUND_ERROR = (
    "L'entreprise n'a pas été trouvée. Vérifiez que le SIREN est correct."
)
TOO_MANY_REQUESTS_ERROR = "Le service est temporairement surchargé. Merci de réessayer."
SERVER_ERROR = "Le service est actuellement indisponible. Merci de réessayer plus tard."


def recherche_unite_legale(siren):
    # documentation api sirene 3.11 https://www.sirene.fr/static-resources/htm/sommaire_311.html
    url = f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}?date={date.today().isoformat()}"
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {API_SIRENE_TOKEN}"},
            timeout=RECHERCHE_ENTREPRISE_TIMEOUT,
        )
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_level("info")
            sentry_sdk.capture_exception(e)
        raise APIError(SERVER_ERROR)

    if response.status_code == 200:
        data = response.json()["uniteLegale"]

        denomination = data["periodesUniteLegale"][0]["denominationUniteLegale"]
        categorie_juridique_sirene = int(
            data["periodesUniteLegale"][0]["categorieJuridiqueUniteLegale"]
        )
        tranche_effectif = int(data["trancheEffectifsUniteLegale"])
        if tranche_effectif < 11:  # moins de 10 salariés
            effectif = CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_10
        elif tranche_effectif < 21:  # moins de 50 salariés
            effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_10_ET_49
        elif tranche_effectif < 32:  # moins de 250 salariés
            effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249
        # la tranche EFFECTIF_ENTRE_250_ET_299 ne peut pas être trouvée avec l'API
        elif tranche_effectif < 41:  # moins de 500 salariés
            effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_300_ET_499
        elif tranche_effectif < 52:  # moins de 5 000 salariés:
            effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_500_ET_4999
        elif tranche_effectif == 52:
            effectif = CaracteristiquesAnnuelles.EFFECTIF_ENTRE_5000_ET_9999
        else:
            effectif = CaracteristiquesAnnuelles.EFFECTIF_10000_ET_PLUS

        return {
            "siren": siren,
            "effectif": effectif,
            "denomination": denomination,
            "categorie_juridique_sirene": categorie_juridique_sirene,
            "code_pays_etranger_sirene": None,
        }
    elif response.status_code == 404:
        raise SirenError(SIREN_NOT_FOUND_ERROR)
    elif response.status_code == 429:
        sentry_sdk.capture_message("Trop de requêtes sur l'API recherche unité légale")
        raise TooManyRequestError(TOO_MANY_REQUESTS_ERROR)
    else:
        sentry_sdk.capture_message("Erreur API recherche unité légale")
        raise ServerError(SERVER_ERROR)
