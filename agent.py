from typing import List


class Agent:
    """Represents a single routing agent moving through the network."""

    def __init__(self, agent_id: str, start_hub: str) -> None:
        """Initialize the agent with its ID and starting zone.

        Args:
            agent_id: Unique identifier for this agent (e.g. 'D1').
            start_hub: Name of the zone where the agent begins.
        """
        self.agent_id = agent_id
        self.current_hub = start_hub
        self.path: List[str] = []
        self.step_index = 0
        self.is_finished = False
        self.has_moved_this_turn = False

        self.travel_time_remaining: int | float = 0
        self.is_in_flight = False

    def get_next_hub_name(self) -> str | None:
        """Return the name of the next hub in the path without advancing.

        Returns:
            Next hub name or None if at the end.
        """
        if self.step_index + 1 < len(self.path):
            return self.path[self.step_index + 1]
        return None

    def set_path(self, path_list: List[str]) -> None:
        """Assign a computed path to this agent.

        Args:
            path_list: Ordered list of zone names from start to end.
        """
        self.path = path_list

    def move_to_next(self, weight: int | float = 1) -> None:
        """Advance the agent one step forward, respecting movement costs.

        Args:
            weight: Movement cost of the destination zone.
        """
        if self.is_finished or self.has_moved_this_turn:
            return None

        if not self.is_in_flight:
            if weight > 1:
                self.is_in_flight = True
                self.travel_time_remaining = weight - 1
            else:
                self.step_index += 1
                self.current_hub = self.path[self.step_index]
        else:
            self.travel_time_remaining -= 1
            if self.travel_time_remaining <= 0:
                self.is_in_flight = False
                self.step_index += 1
                self.current_hub = self.path[self.step_index]

        self.has_moved_this_turn = True

        if self.step_index == len(self.path) - 1:
            self.is_finished = True

    def reset_turn(self) -> None:
        """Reset the move flag at the start of each simulation turn."""
        self.has_moved_this_turn = False
