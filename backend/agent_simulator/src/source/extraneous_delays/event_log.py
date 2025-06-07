from dataclasses import dataclass
from dataclasses import fields
from typing import Optional

import pandas as pd


@dataclass
class EventLogIDs:
    # General
    case: str = "case_id"  # Case ID
    activity: str = "activity_name"  # Activity label
    resource: str = "agent"  # Resource who performed this activity instance
    start_time: str = "start_timestamp"  # Start time of the activity instance
    end_time: str = "end_timestamp"  # End time of the activity instance
    # Start time estimator
    enabled_time: str = "enabled_time"  # Enablement time of the activity instance
    enabling_activity: str = "enabling_activity"  # Label of the activity instance enabling the current one
    available_time: str = (
        "available_time"  # Last availability time of the resource who performed this activity instance
    )
    estimated_start_time: str = "estimated_start_time"  # Estimated start time of the activity instance
    batch_id: str = "batch_instance_id"  # ID of the batch instance this activity instance belongs to, if any
    batch_type: str = "batch_instance_type"  # Type of the batch instance this activity instance belongs to, if any

    @staticmethod
    def from_dict(config: dict) -> "EventLogIDs":
        return EventLogIDs(**config)

    def to_dict(self) -> dict:
        return {attr.name: getattr(self, attr.name) for attr in fields(self.__class__)}


DEFAULT_CSV_IDS = EventLogIDs(
    case="case_id",
    activity="Activity",
    enabled_time="enabled_time",
    start_time="start_time",
    end_time="end_time",
    available_time="available_time",
    estimated_start_time="estimated_start_time",
    resource="Resource",
    batch_id="batch_instance_id",
    batch_type="batch_instance_type",
)
DEFAULT_XES_IDS = EventLogIDs(
    case="case:concept:name",
    activity="concept:name",
    enabled_time="time:enabled",
    start_time="start_timestamp",  # Compatibility with PM4PY
    end_time="time:timestamp",
    available_time="time:available",
    estimated_start_time="time:estimated_start",
    resource="org:resource",
)
APROMORE_LOG_IDS = EventLogIDs(
    case="Case_ID",
    activity="Activity",
    start_time="Start_Time",
    end_time="End_Time",
    resource="Resource",
)
PROSIMOS_LOG_IDS = EventLogIDs(
    case="case_id",
    activity="activity",
    enabled_time="enabled_time",
    start_time="start_time",
    end_time="end_time",
    resource="resource",
)
