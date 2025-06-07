import datetime

import pandas as pd
from source.agent_simulator import AgentSimulator
from source.agent_types.resource_calendar import Interval
from source.agent_types.resource_calendar import RCalendar
from source.arrival_distribution import DistributionType
from source.arrival_distribution import DurationDistribution


def json_to_obj(obj):
    if isinstance(obj, dict):
        if "__type__" in obj:
            type_ = obj["__type__"]

            if type_ == "AgentSimulator":
                agent = AgentSimulator.__new__(AgentSimulator)
                agent.__dict__.update(json_to_obj(obj["data"]))

                # Restore df_train and df_val as DataFrames
                if "df_train" in agent.__dict__:
                    agent.df_train = pd.DataFrame.from_records(agent.df_train)
                if "df_val" in agent.__dict__:
                    agent.df_val = pd.DataFrame.from_records(agent.df_val)

                return agent

            elif type_ == "RCalendar":
                return RCalendar.from_dict(json_to_obj(obj["data"]))

            elif type_ == "DurationDistribution":
                dist = DurationDistribution.__new__(DurationDistribution)
                dist.type = DistributionType(obj["type"])
                dist.mean = obj["mean"]
                dist.var = obj["var"]
                dist.std = obj.get("std")
                dist.min = obj.get("min")
                dist.max = obj.get("max")
                return dist

            elif type_ == "Interval":
                return Interval(
                    start=datetime.datetime.fromisoformat(obj["start"]), end=datetime.datetime.fromisoformat(obj["end"])
                )

            else:
                raise ValueError(f"Unknown type in JSON: {type_}")

        # Normal dict — recursively decode values
        return {k: json_to_obj(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [json_to_obj(item) for item in obj]

    return obj  # Base type (str, int, etc.)
