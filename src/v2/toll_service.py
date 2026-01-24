from typing import Dict, Any
from src.tolls_file import Tolls

class TollServiceV2:

    def __init__(self) -> None:
        self._tolls = Tolls()

    def analyze_route(self, osrm_route: Dict[str, Any]) -> Dict[str, Any]:


        # OSRM attend toujours {"routes": [...]}
        mini_osrm_data = {"routes": [osrm_route]}

        toll_info = self._tolls.get_toll_details(mini_osrm_data)

        return {
            "has_toll": bool(toll_info["has_toll"]),
            "toll_cost": float(toll_info["toll_cost"]),
            "toll_km": float(toll_info["toll_km"]),
            "toll_count": len(toll_info["segments"]),
            "segments": toll_info["segments"],
        }
