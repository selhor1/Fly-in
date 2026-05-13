from typing import Dict, List, Any
from models import HubModel
from map_reader import MapReader


class NetworkGraph:
    """Builds the network graph used during the simulation."""

    def __init__(self, reader: MapReader) -> None:
        """Construct the graph from a parsed map.

        Args:
            reader: A fully parsed MapReader instance.
        """
        self.hubs = reader.hubs
        self.connections = reader.connections

        self.nb_drones = int(reader.nb_drones)

        self.start_name = reader.start
        self.end_name = reader.end

        self.link_capacities: Dict[tuple, int] = {}

        self.adjacencies: Dict[str, List[HubModel]] = \
            {name: [] for name in self.hubs.keys()}

        self._build_graph()

        self.start_node = self.hubs[self.start_name]
        self.end_node = self.hubs[self.end_name]

    def _build_graph(self) -> None:
        """Populate adjacency lists and link capacity map."""
        for conn in self.connections:
            a = conn.hub_a
            b = conn.hub_b

            self.adjacencies[a].append(self.hubs[b])
            self.adjacencies[b].append(self.hubs[a])

            key = tuple(sorted([a, b]))
            self.link_capacities[key] = conn.max_link_capacity

    def get_link_capacity(self, name_a: str, name_b: str) -> int:
        """Return the max simultaneous usage allowed for a given connection.

        Args:
            name_a: First zone name.
            name_b: Second zone name.

        Returns:
            Integer capacity value (default 1).
        """
        key = tuple(sorted([name_a, name_b]))
        return self.link_capacities.get(key, 1)

    def get_color_name(self, hub_name: str) -> str | Any:
        """Return the color label of a zone if defined.

        Args:
            hub_name: Name of the zone.

        Returns:
            Color string or None.
        """
        if hub_name in self.hubs:
            color = self.hubs[hub_name].color
            if color is not None:
                return color.value
        return None
