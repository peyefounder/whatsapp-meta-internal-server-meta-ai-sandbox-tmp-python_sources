import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MPLChartCaptureError:
    chart_type: str
    error_type: str
    error_msg: str

@dataclass
class PythonAction:
    mpl_chart_capture_error: Optional[MPLChartCaptureError] = None

_action_log: List[PythonAction] = []

def record_action(payload):
    if isinstance(payload, MPLChartCaptureError):
        action = PythonAction(mpl_chart_capture_error=payload)
    else:
        raise ValueError("Unsupported action type")

def get_actions() -> List[PythonAction]:
    return _action_log

def clear_actions() -> None:
    _action_log.clear()

def export_actions_to_json() -> Optional[str]:
    def action_to_dict(action: PythonAction) -> dict:
        action_dict = {}
        if action.mpl_chart_capture_error:
            action_dict["mpl_chart_capture_error"] = action.mpl_chart_capture_error.__dict__
        return action_dict

    action_list = [action_to_dict(action) for action in _action_log]
    if not action_list:
        return None
    return json.dumps(action_list)
