import heapq
import math
from typing import Tuple, List, Dict, Any
from slot_manager import SlotManager
from network_graph import NetworkGraph


class Pathfinder:
    """Handles pathfinding across the network using weighted Dijkstra."""

    @staticmethod
    def dijkstra(
        graph: NetworkGraph,
        slots: SlotManager,
        start_turn: int | float = 0,
        max_turns: int = 1000
    ) -> Tuple[Dict[tuple, Any], Any]:
        """Run Dijkstra's algorithm respecting zone and link slot reservations.

        Args:
            graph: The network graph to search.
            slots: Current slot reservation state.
            start_turn: Turn at which this agent begins moving.
            max_turns: Hard cap on simulation turns to prevent infinite loops.

        Returns:
            Tuple of (came_from dict, final_state tuple or None).
        """
        end_hub = graph.hubs[graph.end_name]
        start_dist = math.hypot(
            graph.hubs[graph.start_name].x - end_hub.x,
            graph.hubs[graph.start_name].y - end_hub.y
        )
        queue: list = [(start_turn, 1, start_dist, graph.start_name)]
        visited: set = set()
        visited.add((graph.start_name, start_turn))

        came_from: Dict[tuple, Any] = {(graph.start_name, start_turn): None}
        final_state = None

        while queue:
            current_turn, _, _, current_name = heapq.heappop(queue)

            if current_turn > max_turns:
                break

            if current_name == graph.end_name:
                final_state = (current_name, current_turn)
                break

            # Include wait-in-place as a valid move
            neighbors = list(graph.adjacencies[current_name])
            neighbors.append(graph.hubs[current_name])

            for neighbor in neighbors:
                if neighbor.type.value == 'blocked':
                    continue

                if neighbor.name == current_name:
                    cost: int | float = 1
                else:
                    cost = neighbor.cost

                arrival = current_turn + cost

                hub_free = slots.is_hub_available(neighbor, arrival)
                link_cap = graph.get_link_capacity(current_name, neighbor.name)
                link_free = True

                if neighbor.name != current_name:
                    link_free = slots.is_link_available(
                        current_name, neighbor.name, link_cap, arrival
                    )

                if hub_free and link_free:
                    state = (neighbor.name, arrival)
                    if state not in visited:
                        visited.add(state)
                        came_from[state] = (current_name, current_turn)
                        dist = math.hypot(
                            neighbor.x - end_hub.x,
                            neighbor.y - end_hub.y
                        )
                        priority_flag = (
                            0 if neighbor.type.value == 'priority' else 1
                        )
                        heapq.heappush(
                            queue,
                            (arrival, priority_flag, dist, neighbor.name)
                        )

        return came_from, final_state

    @staticmethod
    def reconstruct_path(
        came_from: Dict[tuple, Any],
        final_state: Any
    ) -> List[str] | None:
        """Rebuild the ordered path from the parent mapping.

        Args:
            came_from: Parent mapping produced by dijkstra().
            final_state: The destination state tuple (name, turn).

        Returns:
            Ordered list of zone names or None if unreachable.
        """
        if final_state not in came_from:
            return None

        path: List[str] = []
        current = final_state

        while current is not None:
            path.append(current[0])
            current = came_from[current]

        return path[::-1]
