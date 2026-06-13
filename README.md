# Ymmo IA

> API secondaire du projet Ymmo, construite avec Flask. Elle alimente le front-end Ymmo avec des trends et des prédictions de ventes basées sur les données récupérées de l'API principale.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

---

## Sommaire

- [Aperçu](#aperçu)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
- [Licence](#licence)

---

## Aperçu

Ymmo IA est l'API de prédiction du projet Ymmo. Elle analyse les transactions immobilières et génère des prédictions de ventes et des tendances pour le front-end et le dashboard agent.

**Consommateurs :**
- Le front-end Ymmo (affichage des trends)
- Le dashboard agent (prédictions par agence)

**Fonctionnalités clés :**
- Prédictions de ventes par zone, type, agence et mois via un modèle **Ridge Regression**
- Analyse des tendances (ventes par zone, type, prix moyen, évolution mensuelle)
- Réentraînement du modèle à la demande via `/retrain`
- CORS activé pour la consommation depuis le front-end

**URL de base :**
```
http://localhost:5100
```

---

## Prérequis

- Python >= 3.10
- pip

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/Zeteox/Ymmo-IA.git
cd Ymmo-IA

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
python main.py
```

L'API est accessible sur [http://localhost:5100](http://localhost:5100).

---

## Configuration

Copiez le fichier d'exemple et renseignez vos variables :

```bash
cp .env.exemple .env
```

| Variable | Description | Exemple |
|----------|-------------|---------|
| `JWT_SECRET` | Secret JWT partagé avec l'API principale | `••••` |
| `AGENT_EMAIL` | Email de l'agent par défaut pour la collecte de données | `defaultagent@gmail.com` |
| `AGENT_PASSWORD` | Mot de passe de l'agent par défaut | `••••` |
| `API_BASE_URL` | URL de base de l'API principale | `http://localhost:8080/api` |


> Ne committez jamais votre `.env` — il est déjà dans le `.gitignore`.

---

## Endpoints

### Prédictions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/predictions` | Prédictions pour tous les groupes le mois suivant |
| `GET` | `/predictions/global` | Prédiction globale du nombre de ventes le mois suivant |
| `GET` | `/predictions/zone/{zone}` | Prédiction pour une zone (ex: `ZONE_CENTRE`) |
| `GET` | `/predictions/type/{type}` | Prédiction pour un type de bien (ex: `HOUSE`) |
| `GET` | `/predictions/zone/{zone}/type/{type}` | Prédiction pour une zone + type |
| `GET` | `/predictions/agency/{agency_id}` | Prédiction de ventes pour une agence |
| `GET` | `/predictions/agency/{agency_id}/forecast?months=3` | Prévision sur N mois (1-12) pour une agence |
| `GET` | `/predictions/all` | Toutes les prédictions agrégées |
| `POST` | `/retrain` | Relance l'analyse et réentraîne le modèle Ridge |

### Tendances

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/trends/zones` | Ventes totales groupées par zone |
| `GET` | `/trends/zones/{zone}` | Ventes pour une zone spécifique |
| `GET` | `/trends/types` | Ventes totales groupées par type de bien |
| `GET` | `/trends/types/{type}` | Ventes pour un type spécifique |
| `GET` | `/trends/zones/{zone}/types` | Tous les types pour une zone donnée |
| `GET` | `/trends/zones/{zone}/types/{type}` | Ventes pour une zone + type précis |
| `GET` | `/trends/prices` | Prix moyen par zone |
| `GET` | `/trends/monthly` | Ventes globales mois par mois |
| `GET` | `/trends/monthly/zones` | Ventes mensuelles groupées par zone |
| `GET` | `/trends/monthly/types` | Ventes mensuelles groupées par type |

---

## Licence

Distribué sous licence **MIT**. Voir [`LICENSE`](LICENSE) pour plus d'informations.