from __future__ import annotations
from typing import Tuple, List, Dict, Any
import requests

def fetch_logs_from_api(endpoint: str, timeout: float = 5.0) -> Tuple[bool, str, List[Dict[str, Any]]]:
    if not endpoint:
        return False, "API Endpoint is empty!", []
    try:
        respons = requests.get(endpoint, timeout=timeout)
        respons.raise_for_status()
        data = respons.json()
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if not isinstance(data, list):
            return False, "API responsonse is not listed!", []
        return True, f"Fetched {len(data)} logs from API.", data
    except requests.exceptions.Timeout:
        return False, "API connection timed out!", []
    except requests.exceptions.ConnectionError as e:
        return False, f"API connection failed: {e}", []
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error: {e}", []
    except ValueError:
        return False, "Failed to parse JSON from API!", []
    except Exception as e:
        return False, f"Unexpected error: {e}", []