import pandas as pd
import joblib
import os
import numpy as np
from datetime import datetime
from sklearn.linear_model import Ridge
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

class Model:
    _Instance = None

    def __init__(self):
        os.makedirs("models", exist_ok=True)

    @staticmethod
    def GetInstance() -> "Model":
        if Model._Instance is None:
            Model._Instance = Model()
        return Model._Instance

    def _TrainSingle(self, csv_path: str, features: list[str], label: str, model_path: str, encoders: dict[str, str]):
        df = pd.read_csv(csv_path)

        fitted_encoders = {}
        for col, pkl_path in encoders.items():
            enc = LabelEncoder()
            df[col] = enc.fit_transform(df[col])
            fitted_encoders[col] = (enc, pkl_path)

        df["month"] = pd.to_datetime(df["month"].astype(str))
        df["month_number"] = df["month"].dt.year * 12 + df["month"].dt.month

        df["month_of_year"] = df["month"].dt.month
        df["month_sin"] = np.sin(2 * np.pi * df["month_of_year"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month_of_year"] / 12)

        base_features = features.copy()
        extra = ["month_sin", "month_cos"]
        all_features = base_features + extra

        X = df[all_features]
        y = df[label]

        model = Ridge(alpha=1.0)

        if len(X) >= 5:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            print(f"[{os.path.basename(model_path)}] MAE: {mae:.2f} (n={len(X)})")
        else:
            model.fit(X, y)
            print(f"[{os.path.basename(model_path)}] entraîné sur {len(X)} lignes (pas de split)")

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        joblib.dump(all_features, model_path.replace(".pkl", "_features.pkl"))

        for col, (enc, pkl_path) in fitted_encoders.items():
            joblib.dump(enc, pkl_path)

    def Train(self):
        self._TrainSingle(
            csv_path="data/stats/monthlySalesByZoneType.csv",
            features=["month_number", "zone", "type"],
            label="sales_count",
            model_path="models/sales_by_zone_type.pkl",
            encoders={
                "zone": "models/zone_encoder.pkl",
                "type": "models/type_encoder.pkl",
            },
        )
        self._TrainSingle(
            csv_path="data/stats/monthlySalesByZone.csv",
            features=["month_number", "zone"],
            label="sales_count",
            model_path="models/sales_by_zone.pkl",
            encoders={"zone": "models/zone_encoder_zone.pkl"},
        )
        self._TrainSingle(
            csv_path="data/stats/monthlySalesByType.csv",
            features=["month_number", "type"],
            label="sales_count",
            model_path="models/sales_by_type.pkl",
            encoders={"type": "models/type_encoder_type.pkl"},
        )
        self._TrainSingle(
            csv_path="data/stats/monthlySales.csv",
            features=["month_number"],
            label="sales_count",
            model_path="models/sales_global.pkl",
            encoders={},
        )

        agency_csv = "data/stats/monthlySalesByAgency.csv"
        if os.path.exists(agency_csv):
            self._TrainSingle(
                csv_path=agency_csv,
                features=["month_number", "agencyId"],
                label="sales_count",
                model_path="models/sales_by_agency.pkl",
                encoders={"agencyId": "models/agency_encoder.pkl"},
            )
        else:
            print("[Model] Warning: monthlySalesByAgency.csv not found — agency model skipped.")

    def _NextMonthNumber(self) -> int:
        now = datetime.now()
        return now.year * 12 + now.month + 1

    def _MonthNumber(self, offset: int = 1) -> int:
        """Return month_number for now + `offset` months (offset=1 → next month)."""
        now = datetime.now()
        return now.year * 12 + now.month + offset

    def _BuildRow(self, month_number: int) -> dict:
        month_of_year = month_number % 12 or 12
        return {
            "month_number": month_number,
            "month_sin":    np.sin(2 * np.pi * month_of_year / 12),
            "month_cos":    np.cos(2 * np.pi * month_of_year / 12),
        }

    def _Predict(self, model_path: str, row: dict) -> int:
        model    = joblib.load(model_path)
        features = joblib.load(model_path.replace(".pkl", "_features.pkl"))
        data     = pd.DataFrame([row])[features]
        result   = model.predict(data)[0]
        return max(0, round(result))

    def PredictNextMonthPerZoneAndType(self, zone: str, type_: str) -> int:
        zoneEncoder = joblib.load("models/zone_encoder.pkl")
        typeEncoder = joblib.load("models/type_encoder.pkl")
        row = {**self._BuildRow(self._NextMonthNumber()),
               "zone": zoneEncoder.transform([zone])[0],
               "type": typeEncoder.transform([type_])[0]}
        return self._Predict("models/sales_by_zone_type.pkl", row)

    def PredictNextMonthPerZone(self, zone: str) -> int:
        zoneEncoder = joblib.load("models/zone_encoder_zone.pkl")
        row = {**self._BuildRow(self._NextMonthNumber()),
               "zone": zoneEncoder.transform([zone])[0]}
        return self._Predict("models/sales_by_zone.pkl", row)

    def PredictNextMonthPerType(self, type_: str) -> int:
        typeEncoder = joblib.load("models/type_encoder_type.pkl")
        row = {**self._BuildRow(self._NextMonthNumber()),
               "type": typeEncoder.transform([type_])[0]}
        return self._Predict("models/sales_by_type.pkl", row)

    def PredictNextMonthGlobal(self) -> int:
        row = self._BuildRow(self._NextMonthNumber())
        return self._Predict("models/sales_global.pkl", row)

    def PredictNextMonthPerAgency(self, agency_id) -> int:
        """Predict sales for a single agency next month."""
        agencyEncoder = joblib.load("models/agency_encoder.pkl")
        row = {**self._BuildRow(self._NextMonthNumber()),
               "agencyId": agencyEncoder.transform([str(agency_id)])[0]}
        return self._Predict("models/sales_by_agency.pkl", row)

    def ForecastAgencyNextMonths(self, agency_id, months: int = 3) -> list[dict]:
        """
        Return a list of { month, predicted } for the next `months` months,
        using the trained Ridge model — no random noise, no ratio tricks.
        """
        agencyEncoder = joblib.load("models/agency_encoder.pkl")
        encoded_id    = agencyEncoder.transform([str(agency_id)])[0]

        result = []
        for offset in range(1, months + 1):
            mn  = self._MonthNumber(offset)
            row = {**self._BuildRow(mn), "agencyId": encoded_id}
            predicted = self._Predict("models/sales_by_agency.pkl", row)
            month_of_year = mn % 12 or 12
            year          = (mn - 1) // 12
            label         = datetime(year, month_of_year, 1).strftime("%B")

            result.append({"month": label, "predicted": predicted})

        return result

    def PredictAllNextMonth(self) -> dict:
        zoneEncoder     = joblib.load("models/zone_encoder.pkl")
        typeEncoder     = joblib.load("models/type_encoder.pkl")
        zoneEncoderZone = joblib.load("models/zone_encoder_zone.pkl")
        typeEncoderType = joblib.load("models/type_encoder_type.pkl")

        zones = list(zoneEncoder.classes_)
        types = list(typeEncoder.classes_)

        result = {
            "global": self.PredictNextMonthGlobal(),
            "by_zone": {
                zone: self.PredictNextMonthPerZone(zone)
                for zone in zoneEncoderZone.classes_
            },
            "by_type": {
                type_: self.PredictNextMonthPerType(type_)
                for type_ in typeEncoderType.classes_
            },
            "by_zone_type": {
                zone: {
                    type_: self.PredictNextMonthPerZoneAndType(zone, type_)
                    for type_ in types
                }
                for zone in zones
            },
        }

        agency_model = "models/sales_by_agency.pkl"
        if os.path.exists(agency_model):
            agencyEncoder = joblib.load("models/agency_encoder.pkl")
            result["by_agency"] = {
                agency_id: self.PredictNextMonthPerAgency(agency_id)
                for agency_id in agencyEncoder.classes_
            }

        return result