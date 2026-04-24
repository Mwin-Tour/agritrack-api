import sqlite3

DATABASE = "agri_track.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS Utilisateurs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe    VARCHAR(255) NOT NULL,
    role            VARCHAR(30)  NOT NULL
                    CHECK(role IN ('admin', 'responsable_entrepot', 'agriculteur')),
    telephone       VARCHAR(20),
    localite        VARCHAR(100),
    date_inscription DATE NOT NULL DEFAULT (DATE('now'))
);

CREATE TABLE IF NOT EXISTS Recoltes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type_produit    VARCHAR(50)  NOT NULL
                    CHECK(type_produit IN ('coton', 'mangue', 'karité')),
    poids_kg        FLOAT        NOT NULL CHECK(poids_kg > 0),
    date            DATE         NOT NULL,
    statut          VARCHAR(20)  NOT NULL DEFAULT 'en_attente'
                    CHECK(statut IN ('en_attente', 'livré', 'rejeté')),
    id_utilisateur  INTEGER NOT NULL REFERENCES Utilisateurs(id)
);
"""

SEED = """
INSERT OR IGNORE INTO Utilisateurs (id, nom, email, mot_de_passe, role, telephone, localite)
VALUES
  (1, 'Admin Système',   'admin@agritrack.bf',  'hash_admin',  'admin',
      'N/A',              'Ouagadougou'),
  (2, 'Kaboré Issouf',   'kabore@agritrack.bf', 'hash_kabore', 'agriculteur',
      '+226 70 00 00 01', 'Koudougou'),
  (3, 'Traoré Ali',      'traore@agritrack.bf', 'hash_traore', 'responsable_entrepot',
      '+226 70 00 00 02', 'Ouagadougou');

INSERT OR IGNORE INTO Recoltes (id, type_produit, poids_kg, date, statut, id_utilisateur)
VALUES
  (1, 'coton',  150.5, '2026-04-15', 'livré',      2),
  (2, 'mangue', 300.0, '2026-04-16', 'livré',      2),
  (3, 'karité',  80.0, '2026-04-17', 'en_attente', 2);
"""


def get_db() -> sqlite3.Connection:
    """Ouvre une connexion SQLite (sans contexte Flask)."""
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables et insère les données de seed."""
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée.")
