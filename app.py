from flask import Flask, request, jsonify
from database import init_db, get_db

app = Flask(__name__)


# ──────────────────────────────────────────
# F4.1 — Enregistrer une nouvelle récolte
# ──────────────────────────────────────────
@app.route("/api/v1/recoltes", methods=["POST"])
def enregistrer_recolte():
    data = request.get_json()

    # Validation des champs obligatoires
    champs_requis = ["type_produit", "poids_kg", "date", "id_utilisateur"]
    for champ in champs_requis:
        if champ not in data:
            return jsonify({"erreur": f"Le champ '{champ}' est obligatoire"}), 400

    type_produit = data["type_produit"]
    poids_kg     = data["poids_kg"]
    date         = data["date"]
    id_utilisateur = data["id_utilisateur"]

    # Validation métier
    produits_valides = ["coton", "mangue", "karité"]
    if type_produit not in produits_valides:
        return jsonify({"erreur": f"Type de produit invalide. Valeurs acceptées : {', '.join(produits_valides)}"}), 400

    if not isinstance(poids_kg, (int, float)) or poids_kg <= 0:
        return jsonify({"erreur": "Le poids doit être supérieur à 0 kg"}), 400

    db = get_db()

    # Vérifier que l'utilisateur existe et est bien agriculteur ou admin
    utilisateur = db.execute(
        "SELECT id, role FROM Utilisateurs WHERE id = ?", (id_utilisateur,)
    ).fetchone()

    if not utilisateur:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404

    if utilisateur["role"] not in ("agriculteur", "admin"):
        return jsonify({"erreur": "Accès refusé : rôle insuffisant"}), 403

    # Insertion en base
    cursor = db.execute(
        """
        INSERT INTO Recoltes (type_produit, poids_kg, date, statut, id_utilisateur)
        VALUES (?, ?, ?, 'en_attente', ?)
        """,
        (type_produit, poids_kg, date, id_utilisateur),
    )
    db.commit()

    return jsonify({
        "message": "Récolte enregistrée avec succès",
        "data": {
            "id": cursor.lastrowid,
            "type_produit": type_produit,
            "poids_kg": poids_kg,
            "date": date,
            "statut": "en_attente",
            "id_utilisateur": id_utilisateur,
        }
    }), 201


# ──────────────────────────────────────────
# F3.3 — Calculer le stock total de l'entrepôt
# ──────────────────────────────────────────
@app.route("/api/v1/entrepot/stock", methods=["GET"])
def stock_entrepot():
    db = get_db()

    # Toutes les récoltes livrées
    recoltes = db.execute(
        """
        SELECT id, type_produit, poids_kg, date
        FROM Recoltes
        WHERE statut = 'livré'
        ORDER BY date DESC
        """
    ).fetchall()

    stock_total = sum(r["poids_kg"] for r in recoltes)

    return jsonify({
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
    }), 200


# ──────────────────────────────────────────
# Démarrage
# ──────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
