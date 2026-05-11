from typing import Dict
from models import HubModel


class SlotManager:
    """Manages turn-based slot reservations for hubs and connections
    to prevent agent collisions during the simulation."""

    def __init__(self) -> None:
        """Initialize empty reservation tables for hubs and connections."""
        self.hub_reservations: Dict[str, Dict[int, int]] = {}
        self.link_reservations: Dict[tuple, Dict[int, int]] = {}

    def is_hub_available(self, hub_obj: HubModel, turn: int) -> bool:
        """Check if a hub has available capacity at the given turn.

        Args:
            hub_obj: The hub model to check.
            turn: The simulation turn number.

        Returns:
            True if the hub has space, False otherwise.
        """
        reserved = self.hub_reservations.get(hub_obj.name, {})
        occupied = reserved.get(turn, 0)
        return occupied < hub_obj.max_drones

    def reserve_hub(self, hub_name: str, turn: int) -> None:
        """Book one slot in a hub at a specific turn.

        Args:
            hub_name: Name of the hub to reserve.
            turn: The simulation turn to book.
        """
        if hub_name not in self.hub_reservations:
            self.hub_reservations[hub_name] = {}
        current = self.hub_reservations[hub_name].get(turn, 0)
        self.hub_reservations[hub_name][turn] = current + 1

    def is_link_available(self, hub_a: str, hub_b: str,
                          limit: int, turn: int) -> bool:
        """Check if the connection between two hubs is free at a given turn.

        Args:
            hub_a: First hub name.
            hub_b: Second hub name.
            limit: Maximum allowed simultaneous usage.
            turn: The simulation turn to check.

        Returns:
            True if the link has capacity, False otherwise.
        """
        key = tuple(sorted([hub_a, hub_b]))
        reserved = self.link_reservations.get(key, {})
        usage = reserved.get(turn, 0)
        return usage < limit

    def reserve_link(self, hub_a: str, hub_b: str, turn: int) -> None:
        """Book one usage slot on a connection at a specific turn.

        Args:
            hub_a: First hub name.
            hub_b: Second hub name.
            turn: The simulation turn to book.
        """
        key = tuple(sorted([hub_a, hub_b]))
        if key not in self.link_reservations:
            self.link_reservations[key] = {}
        current = self.link_reservations[key].get(turn, 0)
        self.link_reservations[key][turn] = current + 1
