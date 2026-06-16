import sys
try:
    from pydantic import BaseModel, Field, field_validator, model_validator
except ModuleNotFoundError:
    print("Pydantic is required. Run: make install")
    sys.exit(0)

try:
    import matplotlib.colors as mcolors
except ModuleNotFoundError:
    print("matplotlib is required. Run: pip install matplotlib")
    sys.exit(0)

from enum import Enum
from typing import Optional
from typing_extensions import Self


class ZoneType(str, Enum):
    """Defines the possible zone types a network node can have."""

    normal = "normal"
    restricted = "restricted"
    priority = "priority"
    blocked = "blocked"


class HubModel(BaseModel):
    """Validates and stores a single zone (hub) in the network."""

    name: str
    x: int
    y: int
    type: ZoneType = Field(default=ZoneType.normal)
    max_drones: int = Field(default=1, ge=1)
    color: Optional[str] = Field(default=None)
    cost: float = Field(default=1.0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure zone names do not contain dashes or spaces."""
        if '-' in v or ' ' in v:
            raise ValueError('Zone name cannot contain "-" or spaces.')
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Ensure the color is a valid color or 'rainbow'."""
        if v is not None:
            v_lower = v.lower()
            if v_lower != 'rainbow' and not mcolors.is_color_like(v_lower):
                raise ValueError(
                    f'Color "{v}" is not a valid color or "rainbow".'
                )
        return v


class ConnectionModel(BaseModel):
    """Validates and stores a bidirectional connection between two zones."""

    hub_a: str
    hub_b: str
    max_link_capacity: int = Field(1, ge=1)

    @field_validator('hub_a', 'hub_b')
    @classmethod
    def validate_hub_names(cls, v: str) -> str:
        """Ensure connected zone names do not contain dashes or spaces."""
        if '-' in v or ' ' in v:
            raise ValueError('Zone name cannot contain "-" or spaces.')
        return v

    @model_validator(mode='after')
    def check_connection_validity(self) -> Self:
        """Ensure a connection links two different zones.
        """
        if self.hub_a == self.hub_b:
            raise ValueError("A connection cannot link a zone to itself.")
        if self.hub_a > self.hub_b:
            self.hub_a, self.hub_b = self.hub_b, self.hub_a
        return self
