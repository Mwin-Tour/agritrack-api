# 🌾 Agri-Track

![CI/CD](https://img.shields.io/github/actions/workflow/status/votre-org/agri-track/ci.yml?branch=main&label=CI%2FCD&style=flat-square)
![Tests](https://img.shields.io/badge/tests-pytest-green?style=flat-square)
![Linter](https://img.shields.io/badge/linter-flake8-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow?style=flat-square)
![License](https://img.shields.io/badge/license-Propriétaire-red?style=flat-square)

> **API de traçabilité agricole** — Du champ à l'entrepôt, chaque récolte compte.

---

## 📖 Description & Contexte

Agri-Track est une API REST conçue pour moderniser la gestion des récoltes au Burkina Faso. Elle permet à une coopérative agricole de **tracer chaque récolte** (coton, mangues, karité) depuis le champ de l'agriculteur jusqu'à l'entrepôt d'exportation.

Aujourd'hui, les informations circulent encore via des registres papier et des appels téléphoniques, entraînant pertes de données, erreurs de stock et manque de transparence. Agri-Track résout ce problème en offrant une **traçabilité numérique de bout en bout**.

**Utilisateurs cibles :**
- 🧑‍🌾 **Agriculteur** — enregistre ses récoltes via l'API
- 🏢 **Gestionnaire de coopérative** — suit les stocks et les données des entrepôts
- 📦 **Responsable d'entrepôt** — consulte la capacité et les récoltes reçues

---

## ⚙️ Prérequis & Installation

### Prérequis

- Python **3.10+**
- `pip` (gestionnaire de paquets Python)
- Git

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-org/agri-track.git
cd agri-track

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
flask db init
flask db migrate -m "init"
flask db upgrade
# ou avec FastAPI :
# python -m app.database

# 5. Lancer le serveur de développement
flask run
# ou avec FastAPI :
# uvicorn app.main:app --reload
```

Le serveur est accessible sur `http://127.0.0.1:5000` (Flask) ou `http://127.0.0.1:8000` (FastAPI).

---

## 🚀 Utilisation & Exemples

### Enregistrer une récolte

```bash
curl -X POST http://localhost:5000/api/recoltes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "agriculteur_id": 1,
    "type_culture": "mangue",
    "poids_kg": 250.5,
    "date_recolte": "2026-04-22",
    "entrepot_id": 3
  }'
```

**Réponse :**
```json
{
  "id": 42,
  "agriculteur_id": 1,
  "type_culture": "mangue",
  "poids_kg": 250.5,
  "statut": "en_attente",
  "created_at": "2026-04-22T10:30:00Z"
}
```

### Calculer le stock total d'un entrepôt

```bash
curl -X GET http://localhost:5000/api/entrepots/3/stock \
  -H "Authorization: Bearer <token>"
```

**Réponse :**
```json
{
  "entrepot_id": 3,
  "stock_total_kg": 12450.75,
  "repartition": {
    "coton": 5000.0,
    "mangue": 4200.75,
    "karite": 3250.0
  }
}
```

### Lister toutes les récoltes

```bash
curl -X GET http://localhost:5000/api/recoltes \
  -H "Authorization: Bearer <token>"
```

> 💡 Consultez la documentation interactive complète sur `/docs` (FastAPI) ou `/api/docs` (Swagger Flask).

---

## 🗂️ Fonctionnalités du MVP

| Module | Fonctionnalités principales |
|---|---|
| **F1 – Utilisateurs & Rôles** | CRUD utilisateurs, gestion des rôles (`admin`, `agriculteur`, `responsable_entrepot`) |
| **F2 – Coopérative** | Consultation et modification des infos de la coopérative |
| **F3 – Entrepôt** | Gestion des entrepôts, calcul du stock total |
| **F4 – Récoltes** | Enregistrement, consultation, modification, suppression ; rejet automatique des poids nuls/négatifs |
| **F5 – Transports** | CRUD des transports de récoltes |
| **F6 – Livraisons** | CRUD des livraisons, gestion des statuts |
| **F7 – Contrôle Qualité** | Création et suivi des contrôles qualité par entrepôt |

---

## 🛠️ Stack Technique

| Outil | Rôle |
|---|---|
| Python + Flask / FastAPI | Développement de l'API REST |
| SQLite | Base de données relationnelle |
| GitHub | Versionnement du code |
| GitHub Actions | Pipeline CI/CD automatisé |
| Pytest | Tests unitaires |
| Flake8 | Linter (qualité du code) |
| Slack | Communication et alertes temps réel |
| Trello / Notion | Gestion de projet |

---

## 🧪 Tests & Qualité du Code

```bash
# Lancer tous les tests unitaires
pytest

# Vérifier la qualité du code avec Flake8
flake8 app/

# Lancer tests + linter en une commande
pytest && flake8 app/
```

Le pipeline CI/CD via **GitHub Actions** exécute automatiquement ces vérifications à chaque `push` et `pull request` sur la branche `main`.

---

## 🤝 Guide de Contribution

1. **Forker** le dépôt et cloner votre fork
2. Créer une branche feature : `git checkout -b feature/nom-de-la-feature`
3. Coder, tester localement (`pytest && flake8 app/`)
4. Commiter avec un message clair : `git commit -m "feat: description courte"`
5. Pousser la branche : `git push origin feature/nom-de-la-feature`
6. Ouvrir une **Pull Request** vers `main` avec une description détaillée

> Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour les conventions de nommage, le processus de review et les règles de résolution de conflits Git.

**Conventions de commits (Conventional Commits) :**
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` mise à jour de la documentation
- `test:` ajout ou modific
ation de tests
- `chore:` tâches de maintenance

---

## 📄 Licence

Ce projet est **propriétaire et confidentiel**. Tous droits réservés © 2026 — Agri-Track / Coopérative Agricole.

Toute reproduction, distribution, modification ou utilisation de ce code, en tout ou en partie, sans autorisation écrite préalable du propriétaire est **strictement interdite**. Ce logiciel est fourni uniquement aux personnes et entités explicitement autorisées.

> Pour toute demande d'accès ou de partenariat, contactez : [contact@agri-track.bf](mailto:contact@agri-track.bf)

---

<p align="center">Fait avec ❤️ au Burkina Faso 🇧🇫 — Agri-Track © 2026</p>
