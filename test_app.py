import pytest
import os
from fastapi.testclient import TestClient

# Utiliser une base de données séparée pour les tests
os.environ["TEST_DB"] = "test_agri_track.db"

from database import init_db, DATABASE  # noqa: E402
import database  # noqa: E402

# Rediriger vers une base de test isolée
database.DATABASE = "test_agri_track.db"

from app import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Recrée la base propre avant chaque test."""
    if os.path.exists("test_agri_track.db"):
        os.remove("test_agri_track.db")
    init_db()
    yield
    if os.path.exists("test_agri_track.db"):
        os.remove("test_agri_track.db")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ─────────────────────────────────────────
# Tests — F4.1 : Enregistrer une récolte
# Carte Trello : #6oIIyKSV
# ─────────────────────────────────────────

def test_enregistrer_recolte_succes(client):
    """Cas nominal : récolte valide créée par un agriculteur."""
    payload = {
        "type_produit": "coton",
        "poids_kg": 120.0,
        "date": "2026-04-22",
        "id_utilisateur": 2,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["data"]["type_produit"] == "coton"
    assert data["data"]["statut"] == "en_attente"


def test_recolte_poids_negatif(client):
    """F4.6 : poids négatif doit être rejeté automatiquement."""
    payload = {
        "type_produit": "mangue",
        "poids_kg": -5,
        "date": "2026-04-22",
        "id_utilisateur": 2,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_poids_nul(client):
    """F4.6 : poids nul doit être rejeté automatiquement."""
    payload = {
        "type_produit": "mangue",
        "poids_kg": 0,
        "date": "2026-04-22",
        "id_utilisateur": 2,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_type_invalide(client):
    """Type de produit hors liste doit retourner une erreur de validation."""
    payload = {
        "type_produit": "maïs",
        "poids_kg": 50.0,
        "date": "2026-04-22",
        "id_utilisateur": 2,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_utilisateur_inexistant(client):
    """Utilisateur introuvable → 404."""
    payload = {
        "type_produit": "coton",
        "poids_kg": 50.0,
        "date": "2026-04-22",
        "id_utilisateur": 999,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 404


def test_recolte_role_insuffisant(client):
    """Responsable entrepôt (id=3) ne peut pas enregistrer une récolte → 403."""
    payload = {
        "type_produit": "coton",
        "poids_kg": 50.0,
        "date": "2026-04-22",
        "id_utilisateur": 3,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 403


def test_recolte_champ_manquant(client):
    """Champ poids_kg absent → erreur de validation 422."""
    payload = {
        "type_produit": "coton",
        "date": "2026-04-22",
        "id_utilisateur": 2,
    }
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


# ─────────────────────────────────────────
# Tests — F3.3 : Stock total entrepôt
# Carte Trello : #6oIIyKSV
# ─────────────────────────────────────────

def test_stock_entrepot_total_correct(client):
    """Le stock total doit correspondre aux récoltes livrées du seed."""
    res = client.get("/api/v1/entrepot/stock")
    assert res.status_code == 200
    data = res.json()
    # Seed : 150.5 (coton) + 300.0 (mangue) = 450.5 kg livrés
    assert data["stock_total_kg"] == 450.5
    assert data["nombre_recoltes"] == 2


def test_stock_exclut_recoltes_en_attente(client):
    """Les récoltes avec statut 'en_attente' ne doivent pas être comptées."""
    res = client.get("/api/v1/entrepot/stock")
    data = res.json()
    ids = [r["id"] for r in data["recoltes"]]
    # Récolte id=3 (karité, en_attente) ne doit pas apparaître
    assert 3 not in ids
