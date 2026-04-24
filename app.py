from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from database import init_db, get_db
from datetime import date


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Agri-Track API",
    version="1.0.0",
    description="Traçabilité des récoltes agricoles — du champ à l'entrepôt",
    lifespan=lifespan,
)


# ──────────────────────────────────────────
# Schémas de validation (Pydantic)
# ──────────────────────────────────────────
class RecolteCreate(BaseModel):
    type_produit: str
    poids_kg: float
    date: date
    id_utilisateur: int

    @field_validator("type_produit")
    @classmethod
    def valider_type_produit(cls, v):
        valides = ["coton", "mangue", "karité"]
        if v not in valides:
            raise ValueError(
                f"Type de produit invalide. Valeurs acceptées : {', '.join(valides)}"
            )
        return v

    @field_validator("poids_kg")
    @classmethod
    def valider_poids(cls, v):
        if v <= 0:
            raise ValueError("Le poids doit être supérieur à 0 kg")
        return v


# ──────────────────────────────────────────
# F4.1 — Enregistrer une nouvelle récolte
# POST /api/v1/recoltes
# Rôle requis : agriculteur, admin
# ──────────────────────────────────────────
@app.post("/api/v1/recoltes", status_code=201)
def enregistrer_recolte(recolte: RecolteCreate):
    with get_db() as db:
        utilisateur = db.execute(
            "SELECT id, role FROM Utilisateurs WHERE id = ?",
            (recolte.id_utilisateur,)
        ).fetchone()

        if not utilisateur:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        if utilisateur["role"] not in ("agriculteur", "admin"):
            raise HTTPException(status_code=403, detail="Accès refusé : rôle insuffisant")

        cursor = db.execute(
            """
            INSERT INTO Recoltes (type_produit, poids_kg, date, statut, id_utilisateur)
            VALUES (?, ?, ?, 'en_attente', ?)
            """,
            (recolte.type_produit, recolte.poids_kg, str(recolte.date), recolte.id_utilisateur),
        )
        db.commit()
        new_id = cursor.lastrowid

    return {
        "message": "Récolte enregistrée avec succès",
        "data": {
            "id": new_id,
            "type_produit": recolte.type_produit,
            "poids_kg": recolte.poids_kg,
            "date": str(recolte.date),
            "statut": "en_attente",
            "id_utilisateur": recolte.id_utilisateur,
        }
    }


# ──────────────────────────────────────────
# F3.3 — Calculer le stock total de l'entrepôt
# GET /api/v1/entrepot/stock
# Rôle requis : admin, responsable_entrepot
# ──────────────────────────────────────────
@app.get("/api/v1/entrepot/stock")
def stock_entrepot():
    with get_db() as db:
        recoltes = db.execute(
            """
            SELECT id, type_produit, poids_kg, date
            FROM Recoltes
            WHERE statut = 'livré'
            ORDER BY date DESC
            """
        ).fetchall()

    stock_total = sum(r["poids_kg"] for r in recoltes)

    return {
        "stock_total_kg": round(stock_total, 2),
        "nombre_recoltes": len(recoltes),
        "recoltes": [
            {
                "id": r["id"],
                "type_produit": r["type_produit"],
                "poids_kg": r["poids_kg"],
                "date": r["date"],
            }
            for r in recoltes
        ],
    }
