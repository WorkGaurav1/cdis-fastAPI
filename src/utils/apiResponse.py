from typing import Any, Dict

def send_success(data: Any = None) -> Dict[str, Any]:
    # Wraps the response in the standard { success: true, data } envelope expected by the frontend.
    return {
        "success": True,
        "data": data if data is not None else {}
    }

def send_error(code: str, message: str) -> Dict[str, Any]:
    # Wraps the error in the standard { success: false, error } envelope.
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
