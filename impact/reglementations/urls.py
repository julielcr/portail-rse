from django.urls import path

from . import views

app_name = "reglementations"
urlpatterns = [
    path("reglementations", views.reglementations, name="reglementations"),
    path("reglementation/<str:siren>", views.reglementation, name="reglementation"),
    path("bdese/<str:siren>/<int:annee>/<int:step>", views.bdese, name="bdese"),
    path("bdese/<str:siren>/<int:annee>/pdf", views.bdese_pdf, name="bdese_pdf"),
    path(
        "bdese/<str:siren>/<int:annee>/actualiser-desactualiser",
        views.toggle_bdese_completion,
        name="toggle_bdese_completion",
    ),
]
