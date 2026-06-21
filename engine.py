from agent import Agent
from pathfinder import Pathfinder
from slot_manager import SlotManager
from palette import TerminalPalette
from network_graph import NetworkGraph
import math
import sys


class Engine:
    """Controls the full lifecycle of a network routing simulation."""

    def __init__(self, graph: NetworkGraph, nb_drones: int) -> None:
        """Set up agents, compute their routes, and register all slot bookings.

        Args:
            graph: The built network graph.
            nb_drones: Total number of agents to route.
        """
        self.graph = graph
        self.nb_drones = nb_drones
        self.turn = 0
        self.slots = SlotManager()
        self.agents: list = []
        self.palette = TerminalPalette()

        for i in range(self.nb_drones):
            max_sim_turns = max(1000, self.nb_drones * 100)
            came_from, final_state = Pathfinder.dijkstra(
                self.graph, self.slots, start_turn=0, max_turns=max_sim_turns
            )
            path = Pathfinder.reconstruct_path(came_from, final_state)

            if path is None:
                print(f"Error: No valid path found for agent D{i + 1}!")
                sys.exit(1)

            new_agent = Agent(
                agent_id=f"D{i + 1}",
                start_hub=self.graph.start_name
            )
            new_agent.set_path(path)
            self.agents.append(new_agent)

            # Pre-register all slot bookings for this agent's path
            current_t: int | float = 0
            for j in range(len(path) - 1):
                u = path[j]
                v = path[j + 1]

                # u == v means the agent waits in place
                if u == v:
                    cost: int | float = 1
                else:
                    dest = self.graph.hubs[v]
                    cost = dest.cost

                arrival_turn = math.ceil(current_t + cost)
                self.slots.reserve_hub(v, arrival_turn)

                if u != v:
                    # Link is used during the turn(s) of transit.
                    # For cost=1, transit turn is arrival_turn.
                    # For cost=2, transit turn is arrival_turn - 1.
                    is_one = (cost == 1)
                    transit_turn = arrival_turn if is_one else arrival_turn - 1
                    self.slots.reserve_link(u, v, int(transit_turn))

                current_t = arrival_turn

    def run(self) -> None:
        """Run the simulation turn by turn until all drones finish."""
        while not all(a.is_finished for a in self.agents):
            self.turn += 1
            turn_moves: list = []

            for agent in self.agents:
                agent.reset_turn()

            # Prioritize agents that are further along their route,
            # and within the same step, prioritize those in-flight (arriving)
            for agent in sorted(
                self.agents,
                key=lambda x: (x.step_index + (1 if x.is_in_flight else 0), x.is_in_flight),
                reverse=True
            ):
                if agent.is_finished:
                    continue

                target_name = agent.get_next_hub_name()
                if target_name is None:
                    continue

                # Waiting in place
                if target_name == agent.current_hub:
                    agent.move_to_next(weight=1)
                    continue

                # Resolve display colors for current and target hubs
                current_color = self.graph.get_color_name(agent.current_hub)
                target_color = self.graph.get_color_name(target_name)

                display_current = agent.current_hub
                display_target = target_name

                if current_color:
                    display_current = self.palette.colorize(
                        agent.current_hub, current_color
                    )
                if target_color:
                    display_target = self.palette.colorize(
                        target_name, target_color
                    )

                target_hub = self.graph.hubs[target_name]
                weight = target_hub.cost

                display_id = agent.agent_id

                if agent.is_in_flight:
                    # Agent is mid-transit toward a restricted zone
                    agent.move_to_next(weight)
                    turn_moves.append(f"{display_id}-{display_target}")
                else:
                    if weight > 1:
                        # Show connection segment for restricted transit
                        turn_moves.append(
                            f"{display_id}-{display_current}-"
                            f"{display_target}"
                        )
                    else:
                        turn_moves.append(
                            f"{display_id}-{display_target}"
                        )

                    agent.move_to_next(weight)

            if turn_moves:
                print(" ".join(turn_moves))

        print(
            "\n" + self.palette.colorize(
                f"{len(self.agents)} drone(s) delivered "
                f"in {self.turn} turn(s).",
                "green"
            )
        )
