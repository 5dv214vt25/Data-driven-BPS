import numpy as np
import pandas as pd
from source.agent_simulator import AgentSimulator  # Adjust to your actual module
from source.agent_types.resource_calendar import Interval
from source.agent_types.resource_calendar import RCalendar
from source.arrival_distribution import DurationDistribution


def agent_to_json(sim_instance):
    def clean_obj(obj):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if k == "df_train" or k == "df_val":
                    continue  # Skip df_train field
                """if k == "transition_probabilities_autonomous":
                continue  # Skip this field"""
                result[str(k)] = clean_obj(v)
            return result

        elif isinstance(obj, list) or isinstance(obj, tuple):
            return [clean_obj(item) for item in obj]

        elif isinstance(obj, AgentSimulator):
            return {"__type__": "AgentSimulator", "data": clean_obj(obj.__dict__)}

        elif isinstance(obj, RCalendar):
            return {"__type__": "RCalendar", "data": clean_obj(obj.to_dict())}

        elif isinstance(obj, pd.DataFrame):
            return obj.applymap(
                lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else (None if pd.isna(x) else x)
            ).to_dict(orient="records")

        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()

        elif isinstance(obj, np.integer):
            return int(obj)

        elif isinstance(obj, np.floating):
            return float(obj)

        elif isinstance(obj, Interval):
            return {"__type__": "Interval", "start": obj.start.isoformat(), "end": obj.end.isoformat()}

        elif isinstance(obj, DurationDistribution):
            return {
                "__type__": "DurationDistribution",
                "type": obj.type.value,
                "mean": obj.mean,
                "var": obj.var,
                "std": obj.std if obj.std is not None else None,
                "min": obj.min,
                "max": obj.max,
            }

        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        # Try using __dict__ if it has one
        if hasattr(obj, "__dict__"):
            return clean_obj(obj.__dict__)

        # Fallback
        return str(obj)

    return clean_obj(sim_instance)
