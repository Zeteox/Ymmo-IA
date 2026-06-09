import csv
from DataCollector import DataCollector
import os
import pandas as pd

class DataAnalyst:
    _Instance = None

    def __init__(self):
        DataCollector.GetInstance().CollectData()
        os.makedirs("data/stats", exist_ok=True)

    @staticmethod
    def GetInstance():
        if DataAnalyst._Instance is None:
            DataAnalyst._Instance = DataAnalyst()
        return DataAnalyst._Instance

    def GetPopularBuildings(self, topN: int = 10) -> list[dict]:
        """
        Retourne les `topN` biens les plus mis en favoris.
        Tri décroissant par favourite_count.
        """
        df = pd.read_csv("data/buildings.csv")

        popular = (
            df[["id", "name", "price", "type", "zone", "state", "favourite_count"]]
            .sort_values("favourite_count", ascending=False)
            .head(topN)
        )

        return popular.to_dict(orient="records")

    def GetPopularZones(self) -> list[dict]:
        """
        Retourne toutes les zones triées par total de favoris décroissant.
        Chaque entrée contient : zone, total_favourites, building_count.
        """
        df = pd.read_csv("data/buildings.csv")

        popular = (
            df.groupby("zone")
            .agg(
                total_favourites=("favourite_count", "sum"),
                building_count=("id", "count"),
            )
            .reset_index()
            .sort_values("total_favourites", ascending=False)
        )

        return popular.to_dict(orient="records")

    def AnalyseData(self):
        transactions = pd.read_csv("data/transactions.csv")
        buildings = pd.read_csv("data/buildings.csv")

        df = transactions.merge(
            buildings,
            left_on="buildingId",
            right_on="id"
        )

        salesByZones = (df.groupby("zone").size().reset_index(name="sales_count").sort_values("sales_count", ascending=False))
        salesByType = (df.groupby("type").size().reset_index(name="sales_count").sort_values("sales_count", ascending=False))
        avgPriceByZone = (df.groupby("zone")["amount"].mean().reset_index(name="average_price"))
        salesByZoneType = (df.groupby(["zone", "type"]).size().reset_index(name="sales_count").sort_values("sales_count", ascending=False))

        salesByZones.to_csv("data/stats/salesByZones.csv", index=False)
        salesByType.to_csv("data/stats/salesByType.csv", index=False)
        avgPriceByZone.to_csv("data/stats/avgPriceByZone.csv", index=False)
        salesByZoneType.to_csv("data/stats/salesByZoneType.csv", index=False)

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        monthlySales = (df.groupby("month").size().reset_index(name="sales_count"))
        monthlySalesByZone = (df.groupby(["month", "zone"]).size().reset_index(name="sales_count"))
        monthlySalesByType = (df.groupby(["month", "type"]).size().reset_index(name="sales_count"))
        monthlySalesByZoneType = (df.groupby(["month", "zone", "type"]).size().reset_index(name="sales_count"))

        monthlySales.to_csv("data/stats/monthlySales.csv", index=False)
        monthlySalesByZone.to_csv("data/stats/monthlySalesByZone.csv", index=False)
        monthlySalesByType.to_csv("data/stats/monthlySalesByType.csv", index=False)
        monthlySalesByZoneType.to_csv("data/stats/monthlySalesByZoneType.csv", index=False)