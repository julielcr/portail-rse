import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from entreprises.models import CaracteristiquesAnnuelles
from habilitations.models import attach_user_to_entreprise
from reglementations.views.base import ReglementationStatus
from reglementations.views.bges import BGESReglementation


def test_bges_reglementation_info():
    info = BGESReglementation.info()

    assert info["title"] == "BGES et plan de transition"

    assert (
        info["description"]
        == "Le bilan GES réglementaire a vocation à contribuer à la mise en œuvre de la stratégie de réduction des émissions de GES des entreprises. Un plan de transition est obligatoirement joint à ce bilan. Il vise à réduire les émissions de gaz à effet de serre et présente les objectifs, moyens et actions envisagées à cette fin ainsi que, le cas échéant, les actions mises en œuvre lors du précédent bilan. Ils sont mis à jour tous les quatre ans."
    )
    assert info["more_info_url"] == reverse("reglementations:fiche_bilan_ges")


@pytest.mark.parametrize("est_soumis", [True, False])
def test_calculate_status_with_not_authenticated_user(
    est_soumis, entreprise_factory, mocker
):
    entreprise = entreprise_factory()
    login_url = f"{reverse('users:login')}?next={reverse('reglementations:reglementations', args=[entreprise.siren])}"

    mocker.patch(
        "reglementations.views.bges.BGESReglementation.est_soumis",
        return_value=est_soumis,
    )
    status = BGESReglementation.calculate_status(
        entreprise.dernieres_caracteristiques_qualifiantes, AnonymousUser()
    )

    if est_soumis:
        assert status.status == ReglementationStatus.STATUS_SOUMIS
        assert (
            status.status_detail
            == f'<a href="{login_url}">Vous êtes soumis à cette réglementation. Connectez-vous pour en savoir plus.</a>'
        )
    else:
        assert status.status == ReglementationStatus.STATUS_NON_SOUMIS
        assert status.status_detail == "Vous n'êtes pas soumis à cette réglementation."
    assert status.primary_action.url == "https://bilans-ges.ademe.fr/bilans"
    assert (
        status.primary_action.title
        == "Consulter les bilans GES sur la plateforme nationale"
    )
    assert status.primary_action.external
    assert status.secondary_actions == []


@pytest.mark.parametrize("est_soumis", [True, False])
def test_calculate_status_with_not_attached_user(
    est_soumis, entreprise_factory, alice, mocker
):
    entreprise = entreprise_factory()

    mocker.patch(
        "reglementations.views.bges.BGESReglementation.est_soumis",
        return_value=est_soumis,
    )
    status = BGESReglementation.calculate_status(
        entreprise.dernieres_caracteristiques_qualifiantes, alice
    )

    if est_soumis:
        assert status.status == ReglementationStatus.STATUS_SOUMIS
        assert (
            status.status_detail == "L'entreprise est soumise à cette réglementation."
        )
    else:
        assert status.status == ReglementationStatus.STATUS_NON_SOUMIS
        assert (
            status.status_detail
            == "L'entreprise n'est pas soumise à cette réglementation."
        )
    assert status.primary_action is None
    assert status.secondary_actions == []


@pytest.mark.parametrize(
    "effectif",
    [
        CaracteristiquesAnnuelles.EFFECTIF_MOINS_DE_50,
        CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249,
        CaracteristiquesAnnuelles.EFFECTIF_ENTRE_300_ET_499,
    ],
)
def test_calcule_le_statut_si_moins_de_500_employes(
    effectif, entreprise_factory, alice
):
    entreprise = entreprise_factory(effectif=effectif)
    attach_user_to_entreprise(alice, entreprise, "Présidente")

    reglementation = BGESReglementation.calculate_status(
        entreprise.dernieres_caracteristiques_qualifiantes, alice
    )

    assert reglementation.status == ReglementationStatus.STATUS_NON_SOUMIS
    assert (
        reglementation.status_detail == "Vous n'êtes pas soumis à cette réglementation"
    )
    assert reglementation.primary_action.url == "https://bilans-ges.ademe.fr/bilans"
    assert (
        reglementation.primary_action.title
        == "Consulter les bilans GES sur la plateforme nationale"
    )
    assert reglementation.primary_action.external


@pytest.mark.parametrize(
    "effectif",
    [
        CaracteristiquesAnnuelles.EFFECTIF_ENTRE_500_ET_4999,
        CaracteristiquesAnnuelles.EFFECTIF_ENTRE_5000_ET_9999,
        CaracteristiquesAnnuelles.EFFECTIF_10000_ET_PLUS,
    ],
)
def test_calcule_le_statut_si_plus_de_500_employes(effectif, entreprise_factory, alice):
    entreprise = entreprise_factory(effectif=effectif)
    attach_user_to_entreprise(alice, entreprise, "Présidente")

    reglementation = BGESReglementation.calculate_status(
        entreprise.dernieres_caracteristiques_qualifiantes, alice
    )

    assert reglementation.status == ReglementationStatus.STATUS_SOUMIS
    assert (
        reglementation.status_detail
        == "Vous êtes soumis à cette réglementation car votre effectif est supérieur à 500 salariés."
    )
    assert (
        reglementation.primary_action.url
        == "https://bilans-ges.ademe.fr/bilans/comment-publier"
    )
    assert (
        reglementation.primary_action.title
        == "Publier mon bilan GES sur la plateforme nationale"
    )
    assert reglementation.primary_action.external


def test_calcule_le_statut_avec_plus_de_250_employes_outre_mer(
    entreprise_factory, alice
):
    entreprise = entreprise_factory(
        effectif=CaracteristiquesAnnuelles.EFFECTIF_ENTRE_50_ET_249,
        effectif_outre_mer=CaracteristiquesAnnuelles.EFFECTIF_OUTRE_MER_250_ET_PLUS,
    )
    attach_user_to_entreprise(alice, entreprise, "Présidente")

    reglementation = BGESReglementation.calculate_status(
        entreprise.dernieres_caracteristiques_qualifiantes, alice
    )

    assert reglementation.status == ReglementationStatus.STATUS_SOUMIS
    assert (
        reglementation.status_detail
        == "Vous êtes soumis à cette réglementation car votre effectif outre-mer est supérieur à 250 salariés."
    )
    assert (
        reglementation.primary_action.title
        == "Publier mon bilan GES sur la plateforme nationale"
    )
