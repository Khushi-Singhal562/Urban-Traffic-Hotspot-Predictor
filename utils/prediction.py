import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR, "models", "traffic_model.pkl"
)

FEATURE_PATH = os.path.join(
    BASE_DIR, "models", "feature_columns.pkl"
)


def load_model():

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    with open(FEATURE_PATH, "rb") as file:
        feature_columns = pickle.load(file)

    return model, feature_columns


def predict_traffic(vehicle_count, average_speed,
                    traffic_density, weather, accident):

    model, feature_columns = load_model()

    input_data = pd.DataFrame([{
        "vehicle_count": vehicle_count,
        "average_speed": average_speed,
        "traffic_density": traffic_density,
        "accident": int(accident)
    }])

    input_data["weather_" + weather] = 1

    input_data = input_data.reindex(
        columns=feature_columns,
        fill_value=0
    )

    prediction = model.predict(input_data)

    return prediction[0]