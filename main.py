from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import os
from dotenv import load_dotenv
from Model import Model
from DataAnalyst import DataAnalyst
import pandas as pd

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
    
@app.route("/predictions/agency/<string:agency_id>/forecast", methods=["GET"])
def forecast_agency(agency_id: str):
    months = request.args.get("months", default=3, type=int)
    months = max(1, min(12, months))
    try:
        return jsonify(Model.GetInstance().ForecastAgencyNextMonths(agency_id, months))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
 
@app.route("/predictions/all", methods=["GET"])
def predict_all():
    try:
        return jsonify(Model.GetInstance().PredictAllNextMonth())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
 
@app.route("/predictions/agency/<string:agency_id>", methods=["GET"])
def predict_agency(agency_id: str):
    try:
        return jsonify({
            "agency_id": agency_id,
            "predicted": Model.GetInstance().PredictNextMonthPerAgency(agency_id)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/retrain", methods=["POST"])
def Retrain():
    """
    Relance l'analyse + réentraîne les modèles.
    Utile quand de nouvelles transactions arrivent.
    """
    analyst.AnalyseData()
    model.Train()
    return jsonify({ "status": "ok", "message": "Modèles réentraînés." })

@app.route("/trends/zones", methods=["GET"])
def GetSalesByZones():
    """Ventes totales groupées par zone."""
    df = pd.read_csv("data/stats/salesByZones.csv")
    return jsonify(df.to_dict(orient="records"))

 
@app.route("/trends/zones/<string:zone>", methods=["GET"])
def GetSalesByZone(zone: str):
    """Ventes pour une zone spécifique. Exemple : /trends/zones/ZONE_CENTRE"""
    df = pd.read_csv("data/stats/salesByZones.csv")
    result = df[df["zone"] == zone]
    if result.empty:
        return jsonify({ "error": f"Zone '{zone}' inconnue." }), 404
    return jsonify(result.iloc[0].to_dict())
 
 
@app.route("/trends/types", methods=["GET"])
def GetSalesByTypes():
    """Ventes totales groupées par type de bien."""
    df = pd.read_csv("data/stats/salesByType.csv")
    return jsonify(df.to_dict(orient="records"))
 
 
@app.route("/trends/types/<string:type_>", methods=["GET"])
def GetSalesByType(type_: str):
    """Ventes pour un type spécifique. Exemple : /trends/types/APARTMENT"""
    df = pd.read_csv("data/stats/salesByType.csv")
    result = df[df["type"] == type_]
    if result.empty:
        return jsonify({ "error": f"Type '{type_}' inconnu." }), 404
    return jsonify(result.iloc[0].to_dict())
 
 
@app.route("/trends/zones/<string:zone>/types", methods=["GET"])
def GetSalesByZoneTypes(zone: str):
    """Tous les types pour une zone donnée. Exemple : /trends/zones/ZONE_CENTRE/types"""
    df = pd.read_csv("data/stats/salesByZoneType.csv")
    result = df[df["zone"] == zone]
    if result.empty:
        return jsonify({ "error": f"Zone '{zone}' inconnue." }), 404
    return jsonify(result.to_dict(orient="records"))
 
 
@app.route("/trends/zones/<string:zone>/types/<string:type_>", methods=["GET"])
def GetSalesByZoneAndType(zone: str, type_: str):
    """Ventes pour une zone + type précis. Exemple : /trends/zones/ZONE_CENTRE/types/HOUSE"""
    df = pd.read_csv("data/stats/salesByZoneType.csv")
    result = df[(df["zone"] == zone) & (df["type"] == type_)]
    if result.empty:
        return jsonify({ "error": f"Combinaison zone='{zone}' / type='{type_}' inconnue." }), 404
    return jsonify(result.iloc[0].to_dict())
 
 
@app.route("/trends/prices", methods=["GET"])
def GetAvgPriceByZone():
    """Prix moyen par zone."""
    df = pd.read_csv("data/stats/avgPriceByZone.csv")
    return jsonify(df.to_dict(orient="records"))
 
 
@app.route("/trends/monthly", methods=["GET"])
def GetMonthlySales():
    """Ventes globales mois par mois."""
    df = pd.read_csv("data/stats/monthlySales.csv")
    return jsonify(df.to_dict(orient="records"))
 
 
@app.route("/trends/monthly/zones", methods=["GET"])
def GetMonthlySalesByZone():
    """Ventes mois par mois, groupées par zone."""
    df = pd.read_csv("data/stats/monthlySalesByZone.csv")
    return jsonify(df.to_dict(orient="records"))
 
 
@app.route("/trends/monthly/types", methods=["GET"])
def GetMonthlySalesByType():
    """Ventes mois par mois, groupées par type."""
    df = pd.read_csv("data/stats/monthlySalesByType.csv")
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, port=5100)