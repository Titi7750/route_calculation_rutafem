import requests


url = "http://router.project-osrm.org/route/v1/driving/2.3522,48.8566;4.8357,45.7640"
params = {"steps": "true", "overview": "full"}

response = requests.get(url, params=params)
data = response.json()


refs_found = []
for route in data.get("routes", []):
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            ref = step.get("ref", "")
            if ref:
                refs_found.append(ref)
                print(f" Ref trouvé: {ref} - {step.get('name', 'N/A')}")
            else:
                name = step.get("name", "")
                if "A" in name or "Autoroute" in name.lower():
                    print(f" Pas de ref mais nom suspect: {name}")

print(f"\n Total refs trouvés: {len(refs_found)}")
print(f"Refs: {set(refs_found)}")