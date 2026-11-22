
import os
import requests
from dotenv import load_dotenv

# Project ke main folder se .env file load karo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

def get_live_traffic(latitude, longitude):

    if not TOMTOM_API_KEY:
        raise ValueError("TomTom API key .env file mein nahi mili.")

    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

    params = {
        "key": TOMTOM_API_KEY,
        "point": f"{latitude},{longitude}",
        "unit": "kmph"
    }

    # TomTom API request
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    # Testing ke liye raw response terminal mein show hoga
    print("\nTOMTOM RAW RESPONSE:")
    print(data)

    # API response check
    if "flowSegmentData" not in data:
        raise ValueError(
            "TomTom response mein flowSegmentData nahi mila: "
            + str(data)[:1000]
        )

    flow = data["flowSegmentData"]

    if "currentSpeed" not in flow:
        raise ValueError(
            "TomTom response mein currentSpeed nahi mila: "
            + str(flow)[:1000]
        )

    current_speed = flow["currentSpeed"]
    free_flow_speed = flow.get("freeFlowSpeed", 0)

    # Congestion percentage calculate karo
    if free_flow_speed > 0:
        congestion = (
            (free_flow_speed - current_speed) / free_flow_speed
        ) * 100
        congestion = max(0, min(100, congestion))
    else:
        congestion = 0

    # Traffic level
    if congestion >= 60:
        traffic_level = "High"
    elif congestion >= 30:
        traffic_level = "Medium"
    else:
        traffic_level = "Low"

    return {
        "current_speed": current_speed,
        "free_flow_speed": free_flow_speed,
        "congestion": round(congestion, 2),
        "traffic_level": traffic_level,
        "confidence": flow.get("confidence"),
        "road_closure": flow.get("roadClosure")
    }
