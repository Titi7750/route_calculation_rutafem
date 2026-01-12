from typing import Dict, List

# Autoroutes 
TOLL_MOTORWAYS = {
    "A1","A2","A3","A4","A5","A6","A6A","A6B","A7","A8","A9",
    "A10","A11","A13","A14","A16","A19","A20","A26","A28",
    "A29","A31","A36","A39","A40","A43","A48","A49",
    "A61","A62","A63","A71","A83","A84","A89"
}

# Tarif estimé
TOLL_RATES = {
    "A6": 0.112,
    "A7": 0.128,
    "A8": 0.135,
    "A10": 0.108,
    "A11": 0.110,
    "A13": 0.115,
    "A31": 0.098,
    "A40": 0.115,
    "A61": 0.095,
    "A71": 0.095,
    "A89": 0.105
}

DEFAULT_RATE = 0.11


def normalize_ref(ref: str) -> str:
    """Supprime espaces : 'A 6' → 'A6'"""
    return ref.replace(" ", "").upper()


def extract_toll_segments(osrm_data: Dict) -> List[Dict]:
    """Détecte les segments à péage via OSRM"""
    segments = []

    for route in osrm_data.get("routes", []):
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                raw_ref = step.get("ref", "")
                distance = step.get("distance", 0)

                if not raw_ref or distance <= 0:
                    continue

                refs = [normalize_ref(r) for r in raw_ref.split(";")]

                for ref in refs:
                    if ref in TOLL_MOTORWAYS:
                        segments.append({
                            "motorway": ref,
                            "distance_km": round(distance / 1000, 3)
                        })
                        break

    return segments


def compute_toll_cost(segments: List[Dict]) -> float:
    """Calcule le coût total des péages"""
    total = 0.0

    for seg in segments:
        motorway = seg["motorway"]
        km = seg["distance_km"]
        rate = TOLL_RATES.get(motorway, DEFAULT_RATE)
        total += km * rate

    return round(total, 2)


def estimate_route_toll(osrm_data: Dict) -> Dict:
    """Pipeline final péages"""
    segments = extract_toll_segments(osrm_data)

    if not segments:
        return {
            "has_toll": False,
            "toll_km": 0.0,
            "toll_cost": 0.0,
            "segments": []
        }

    total_km = round(sum(s["distance_km"] for s in segments), 2)
    cost = compute_toll_cost(segments)

    return {
        "has_toll": True,
        "toll_km": total_km,
        "toll_cost": cost,
        "segments": segments
    }
