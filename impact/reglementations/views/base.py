from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

from django.conf import settings
from django.urls import reverse_lazy

from entreprises.models import CaracteristiquesAnnuelles
from habilitations.models import is_user_attached_to_entreprise


@dataclass
class ReglementationAction:
    url: str
    title: str
    external: bool = False


@dataclass
class ReglementationStatus:
    STATUS_A_ACTUALISER = 0
    STATUS_EN_COURS = 1
    STATUS_A_JOUR = 2
    STATUS_SOUMIS = 3
    STATUS_NON_SOUMIS = 4

    status: int
    status_detail: str
    primary_action: ReglementationAction | None = None
    secondary_actions: list[ReglementationAction] = field(default_factory=list)


class Reglementation(ABC):
    title: str
    description: str
    more_info_url: str

    @classmethod
    def info(cls):
        return {
            "title": cls.title,
            "description": cls.description,
            "more_info_url": cls.more_info_url,
        }

    @classmethod
    @abstractmethod
    def est_soumis(cls, caracteristiques: CaracteristiquesAnnuelles) -> bool:
        pass

    @classmethod
    @abstractmethod
    def calculate_status(
        cls,
        caracteristiques: CaracteristiquesAnnuelles,
        user: settings.AUTH_USER_MODEL,
    ) -> ReglementationStatus:
        if not user.is_authenticated:
            return cls.calculate_status_for_anonymous_user(caracteristiques)
        elif not is_user_attached_to_entreprise(user, caracteristiques.entreprise):
            return cls.calculate_status_for_unauthorized_user(caracteristiques)

    @classmethod
    def calculate_status_for_anonymous_user(
        cls, caracteristiques: CaracteristiquesAnnuelles, primary_action=None
    ):
        if cls.est_soumis(caracteristiques):
            status = ReglementationStatus.STATUS_SOUMIS
            login_url = f"{reverse_lazy('users:login')}?next={reverse_lazy('reglementations:reglementations', args=[caracteristiques.entreprise.siren])}"
            status_detail = f'<a href="{login_url}">Vous êtes soumis à cette réglementation. Connectez-vous pour en savoir plus.</a>'
        else:
            status = ReglementationStatus.STATUS_NON_SOUMIS
            status_detail = "Vous n'êtes pas soumis à cette réglementation."
        return ReglementationStatus(
            status, status_detail, primary_action=primary_action
        )

    @classmethod
    def calculate_status_for_unauthorized_user(
        cls, caracteristiques: CaracteristiquesAnnuelles
    ):
        if cls.est_soumis(caracteristiques):
            status = ReglementationStatus.STATUS_SOUMIS
            status_detail = "L'entreprise est soumise à cette réglementation."
        else:
            status = ReglementationStatus.STATUS_NON_SOUMIS
            status_detail = "L'entreprise n'est pas soumise à cette réglementation."
        return ReglementationStatus(status, status_detail)
