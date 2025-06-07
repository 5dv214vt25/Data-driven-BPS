from dataclasses import asdict
from dataclasses import dataclass
from typing import List


@dataclass
class Resource:
    """Simulation resource compatible with Prosimos."""

    id: str
    name: str
    amount: int
    cost_per_hour: float
    calendar_id: str
    assigned_tasks: List[str]

    @staticmethod
    def from_dict(resource: dict) -> "Resource":
        return Resource(
            id=resource["id"],
            name=resource["name"],
            amount=int(resource["amount"]),
            cost_per_hour=float(resource["cost_per_hour"]),
            calendar_id=resource["calendar"],
            assigned_tasks=resource["assignedTasks"],
        )


@dataclass
class ResourceProfile:
    """Simulation resource profile compatible with Prosimos."""

    id: str
    name: str
    resources: List[Resource]

    def to_dict(self) -> dict:
        """Dictionary with the structure compatible with Prosimos:"""
        result = asdict(self)

        # renaming for Prosimos
        result["resource_list"] = result.pop("resources")
        for resource in result["resource_list"]:
            resource["calendar"] = resource.pop("calendar_id")
            resource["assignedTasks"] = resource.pop("assigned_tasks")

        return result

    @staticmethod
    def from_dict(resource_profile: dict) -> "ResourceProfile":
        return ResourceProfile(
            id=resource_profile["id"],
            name=resource_profile["name"],
            resources=[Resource.from_dict(resource) for resource in resource_profile["resource_list"]],
        )
