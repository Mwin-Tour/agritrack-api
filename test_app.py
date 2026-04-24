from fastapi.testclient import TestClient
from app import app
from database import init_db

client = TestClient(app)


def setup_function():
    """Réinitialise la base avant chaque test."""
    init_db()


# ─────────────────────────────────────────
# Tests — F4.1 : Enregistrer une récolte
# Branche : feature/api-enregistrement
# Carte Trello : #6oIIyKSV
# ─────────────────────────────────────────

def test_enregistrer_recolte_succes():
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


def test_recolte_poids_negatif():
    """F4.6 : poids négatif doit être rejeté automatiquement."""
    payload = {"type_produit": "mangue", "poids_kg": -5, "date": "2026-04-22", "id_utilisateur": 2}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_poids_nul():
    """F4.6 : poids nul doit être rejeté automatiquement."""
    payload = {"type_produit": "mangue", "poids_kg": 0, "date": "2026-04-22", "id_utilisateur": 2}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_type_invalide():
    """Type de produit hors liste doit retourner une erreur de validation."""
    payload = {"type_produit": "maïs", "poids_kg": 50.0, "date": "2026-04-22", "id_utilisateur": 2}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


def test_recolte_utilisateur_inexistant():
    """Utilisateur introuvable → 404."""
    payload = {"type_produit": "coton", "poids_kg": 50.0, "date": "2026-04-22", "id_utilisateur": 999}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 404


def test_recolte_role_insuffisant():
    """Responsable entrepôt (id=3) ne peut pas enregistrer une récolte → 403."""
    payload = {"type_produit": "coton", "poids_kg": 50.0, "date": "2026-04-22", "id_utilisateur": 3}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 403


def test_recolte_champ_manquant():
    """Champ poids_kg absent → erreur de validation 422."""
    payload = {"type_produit": "coton", "date": "2026-04-22", "id_utilisateur": 2}
    res = client.post("/api/v1/recoltes", json=payload)
    assert res.status_code == 422


# ─────────────────────────────────────────
# Tests — F3.3 : Stock total entrepôt
# Branche : feature/calcul-stock
# Carte Trello : #6oIIyKSV
# ─────────────────────────────────────────

def test_stock_entrepot_total_correct():
    """Le stock total doit correspondre aux récoltes livrées du seed."""
    res = client.get("/api/v1/entrepot/stock")
    assert res.status_code == 200
    data = res.json()
    # Seed : 150.5 (coton) + 300.0 (mangue) = 450.5 kg livrés
    assert data["stock_total_kg"] == 450.5
    assert data["nombre_recoltes"] == 2


def test_stock_exclut_recoltes_en_attente():
    """Les récoltes avec statut 'en_attente' ne doivent pas être comptées."""
    res = client.get("/api/v1/entrepot/stock")
    data = res.json()
    ids = [r["id"] for r in data["recoltes"]]
    # Récolte id=3 (karité, en_attente) ne doit pas apparaître
    assert 3 not in ids
