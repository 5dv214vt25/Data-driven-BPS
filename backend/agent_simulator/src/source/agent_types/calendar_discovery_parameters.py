from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Method(Enum):
    TRAPEZOIDAL = 0
    POINT = 1
    UNFIXED_INTERVALS = 2


str_week_days = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}

int_week_days = {
    0: "MONDAY",
    1: "TUESDAY",
    2: "WEDNESDAY",
    3: "THURSDAY",
    4: "FRIDAY",
    5: "SATURDAY",
    6: "SUNDAY",
}

conversion_table = {
    "WEEKS": 604800,
    "DAYS": 86400,
    "HOURS": 3600,
    "MINUTES": 60,
    "SECONDS": 1,
}


class CalendarType(str, Enum):
    DEFAULT_24_7 = "24/7"  # 24/7 work day
    DEFAULT_9_5 = "9/5"  # 9 to 5 work day
    UNDIFFERENTIATED = "undifferentiated"
    DIFFERENTIATED_BY_POOL = "differentiated_by_pool"
    DIFFERENTIATED_BY_RESOURCE = "differentiated_by_resource"
    DIFFERENTIATED_BY_RESOURCE_FUZZY = "differentiated_by_resource_fuzzy"

    @classmethod
    def from_str(cls, value: str) -> "CalendarType":
        if value.lower() in ("default_24_7", "dt247", "24_7", "247"):
            return cls.DEFAULT_24_7
        elif value.lower() in ("default_9_5", "dt95", "9_5", "95"):
            return cls.DEFAULT_9_5
        elif value.lower() == "undifferentiated":
            return cls.UNDIFFERENTIATED
        elif value.lower() in ("differentiated_by_pool", "pool", "pooled"):
            return cls.DIFFERENTIATED_BY_POOL
        elif value.lower() in ("differentiated_by_resource", "differentiated"):
            return cls.DIFFERENTIATED_BY_RESOURCE
        elif value.lower() in ("differentiated_by_resource_fuzzy", "differentiated_fuzzy"):
            return cls.DIFFERENTIATED_BY_RESOURCE_FUZZY
        else:
            raise ValueError(f"Unknown value {value}")

    def __str__(self):
        if self == CalendarType.DEFAULT_24_7:
            return "default_24_7"
        elif self == CalendarType.DEFAULT_9_5:
            return "default_9_5"
        elif self == CalendarType.UNDIFFERENTIATED:
            return "undifferentiated"
        elif self == CalendarType.DIFFERENTIATED_BY_POOL:
            return "differentiated_by_pool"
        elif self == CalendarType.DIFFERENTIATED_BY_RESOURCE:
            return "differentiated_by_resource"
        elif self == CalendarType.DIFFERENTIATED_BY_RESOURCE_FUZZY:
            return "differentiated_by_resource_fuzzy"
        return f"Unknown CalendarType {str(self)}"


@dataclass
class CalendarDiscoveryParameters:
    discovery_type: CalendarType = CalendarType.UNDIFFERENTIATED  # CalendarType.UNDIFFERENTIATED
    granularity: Optional[int] = 60  # minutes per granule
    confidence: Optional[float] = 0.1  # from 0 to 1.0
    support: Optional[float] = 0.1  # from 0 to 1.0
    participation: Optional[float] = 0.4  # from 0 to 1.0

    # Parameters unique to fuzzy calendars (it uses granularity too)
    fuzzy_method: Optional[Method] = Method.TRAPEZOIDAL
    fuzzy_angle: Optional[float] = 1.0

    def to_dict(self) -> dict:
        calendar_discovery_params = {"discovery_type": self.discovery_type.value}

        if self.discovery_type in [
            CalendarType.UNDIFFERENTIATED,
            CalendarType.DIFFERENTIATED_BY_RESOURCE,
            CalendarType.DIFFERENTIATED_BY_POOL,
        ]:
            calendar_discovery_params["granularity"] = self.granularity
            calendar_discovery_params["confidence"] = self.confidence
            calendar_discovery_params["support"] = self.support
            calendar_discovery_params["participation"] = self.participation
        elif self.discovery_type == CalendarType.DIFFERENTIATED_BY_RESOURCE_FUZZY:
            calendar_discovery_params["granularity"] = self.granularity
            calendar_discovery_params["fuzzy_method"] = self.fuzzy_method.value
            calendar_discovery_params["fuzzy_angle"] = self.fuzzy_angle

        return calendar_discovery_params

    @staticmethod
    def from_dict(calendar_discovery_params: dict) -> "CalendarDiscoveryParameters":
        granularity = None
        confidence = None
        support = None
        participation = None
        fuzzy_method = None
        fuzzy_angle = None

        # If the discovery type implies a discovery, parse parameters
        if calendar_discovery_params["discovery_type"] in [
            CalendarType.UNDIFFERENTIATED,
            CalendarType.DIFFERENTIATED_BY_RESOURCE,
            CalendarType.DIFFERENTIATED_BY_POOL,
        ]:
            granularity = calendar_discovery_params["granularity"]
            confidence = calendar_discovery_params["confidence"]
            support = calendar_discovery_params["support"]
            participation = calendar_discovery_params["participation"]
        elif calendar_discovery_params["discovery_type"] == CalendarType.DIFFERENTIATED_BY_RESOURCE_FUZZY:
            granularity = calendar_discovery_params["granularity"]
            fuzzy_method = Method.from_str(calendar_discovery_params["fuzzy_method"])
            fuzzy_angle = calendar_discovery_params["angle"]

        return CalendarDiscoveryParameters(
            discovery_type=calendar_discovery_params["discovery_type"],
            granularity=granularity,
            confidence=confidence,
            support=support,
            participation=participation,
            fuzzy_method=fuzzy_method,
            fuzzy_angle=fuzzy_angle,
        )
