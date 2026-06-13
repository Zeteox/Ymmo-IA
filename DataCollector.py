import csv
from dotenv import load_dotenv
import requests
import os
from collections import Counter

load_dotenv()

class DataCollector:
    BASE_URL = os.getenv("API_BASE_URL")

    endpoints = {
        "login": "/auth/login",
        "users": "/users",
        "transactions": "/transactions",
        "favourites": "/favourites",
        "buildings": "/buildings",
        "agencies": "/agencies",
    }

    _Instance = None

    def __init__(self):
        os.makedirs("data", exist_ok=True)

    @staticmethod
    def GetInstance():
        if DataCollector._Instance is None:
            DataCollector._Instance = DataCollector()
        return DataCollector._Instance

    def CollectData(self):
        logReq = requests.post(
            f"{self.BASE_URL}{self.endpoints['login']}",
            json={"email": os.getenv("AGENT_EMAIL"), "password": os.getenv("AGENT_PASSWORD")},
        )
        token = logReq.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        users        = requests.get(f"{self.BASE_URL}{self.endpoints['users']}", headers=headers).json()
        transactions = requests.get(f"{self.BASE_URL}{self.endpoints['transactions']}", headers=headers).json()
        buildings    = requests.get(f"{self.BASE_URL}{self.endpoints['buildings']}", headers=headers).json()
        agencies     = requests.get(f"{self.BASE_URL}{self.endpoints['agencies']}", headers=headers).json()

        favourite_building_ids = []
        for user in users:
            user_id = user["id"]
            resp = requests.get(f"{self.BASE_URL}/users/{user_id}/favorites", headers=headers)
            if resp.ok:
                favourites = resp.json()
                for fav in favourites:
                    favourite_building_ids.append(fav.get("id"))

        favourite_counts = Counter(favourite_building_ids)

        for building in buildings:
            building["favourite_count"] = favourite_counts.get(building["id"], 0)

        if len(users) > 0:
            with open("data/users.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=users[0].keys())
                writer.writeheader()
                writer.writerows(users)

        if len(transactions) > 0:
            with open("data/transactions.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=transactions[0].keys())
                writer.writeheader()
                writer.writerows(transactions)

        if len(buildings) > 0:
            with open("data/buildings.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=buildings[0].keys())  # favourite_count inclus automatiquement
                writer.writeheader()
                writer.writerows(buildings)

        if len(agencies) > 0:
            with open("data/agencies.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=agencies[0].keys())
                writer.writeheader()
                writer.writerows(agencies)

        print(f"Saved {len(users)} users to users.csv")
        print(f"Saved {len(transactions)} transactions to transactions.csv")
        print(f"Saved {len(buildings)} buildings to buildings.csv")
        print(f"Saved {len(agencies)} agencies to agencies.csv")