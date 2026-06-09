import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import os
from dotenv import load_dotenv
from Model import Model
from DataAnalyst import DataAnalyst

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

app = Flask("Ymmo-IAPI")

analyst = DataAnalyst.GetInstance()
analyst.AnalyseData()

model = Model.GetInstance()
model.Train()

CORS(app)

@app.route("/predictions", methods=["GET"])
def GetAllPredictions():
    """Toutes les prédictions pour le mois suivant."""
    return jsonify(model.PredictAllNextMonth())


@app.route("/predictions/global", methods=["GET"])
def GetGlobalPrediction():
    """Prédiction globale pour le mois suivant."""
    return jsonify({ "sales_count": model.PredictNextMonthGlobal() })


@app.route("/predictions/zone/<string:zone>", methods=["GET"])
def GetPredictionByZone(zone: str):
    """
    Prédiction pour une zone spécifique.
    Exemple : /predictions/zone/ZONE_CENTRE
    """
    try:
        return jsonify({ "zone": zone, "sales_count": model.PredictNextMonthPerZone(zone) })
    except ValueError:
        return jsonify({ "error": f"Zone '{zone}' inconnue." }), 404


@app.route("/predictions/type/<string:type_>", methods=["GET"])
def GetPredictionByType(type_: str):
    """
    Prédiction pour un type de bâtiment spécifique.
    Exemple : /predictions/type/HOUSE
    """
    try:
        return jsonify({ "type": type_, "sales_count": model.PredictNextMonthPerType(type_) })
    except ValueError:
        return jsonify({ "error": f"Type '{type_}' inconnu." }), 404


@app.route("/predictions/zone/<string:zone>/type/<string:type_>", methods=["GET"])
def GetPredictionByZoneAndType(zone: str, type_: str):
    """
    Prédiction pour une zone + type spécifique.
    Exemple : /predictions/zone/ZONE_CENTRE/type/HOUSE
    """
    try:
        return jsonify({
            "zone":        zone,
            "type":        type_,
            "sales_count": model.PredictNextMonthPerZoneAndType(zone, type_)
        })
    except ValueError as e:
        return jsonify({ "error": str(e) }), 404


@app.route("/retrain", methods=["POST"])
def Retrain():
    """
    Relance l'analyse + réentraîne les modèles.
    Utile quand de nouvelles transactions arrivent.
    """
    analyst.AnalyseData()
    model.Train()
    return jsonify({ "status": "ok", "message": "Modèles réentraînés." })

if __name__ == "__main__":
    app.run(debug=True, port=5100)