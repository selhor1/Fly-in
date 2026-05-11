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
            came_from, final_state = Pathfinder.dijkstra(
                self.graph, self.slots, start_turn=0
            )
            path = Pathfinder.reconstruct_path(came_from, final_state)

            if path is None:
                print(f"Error: No valid path found for agent D{i + 1}!")
                sys.exit(0)

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
                    if dest.type.value == 'restricted':
                        cost = 2
                    elif dest.type.value == 'priority':
                        cost = 0.9
                    else:
                        cost = 1

                arrival_turn = math.ceil(current_t + cost)
                self.slots.reserve_hub(v, arrival_turn)

                if u != v:
                    self.slots.reserve_link(u, v, arrival_turn)

                current_t = arrival_turn

    def run(self) -> None:
        """Run the simulation turn by turn until all agents reach the destination.

        Output format per subject:
            D<ID>-<zone>             normal move
            D<ID>-<from>-<to>        agent in transit toward restricted zone
        """
        while not all(a.is_finished for a in self.agents):
            self.turn += 1
            turn_moves: list = []

            for agent in self.agents:
                agent.reset_turn()

            # Prioritize agents that are further along their route
            for agent in sorted(
                self.agents, key=lambda x: x.step_index, reverse=True
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
                target_color  = self.graph.get_color_name(target_name)

                display_current = agent.current_hub
                display_target  = target_name

                if current_color:
                    display_current = self.palette.colorize(
                        agent.current_hub, current_color
                    )
                if target_color:
                    display_target = self.palette.colorize(
                        target_name, target_color
                    )

                target_hub = self.graph.hubs[target_name]

                if target_hub.type.value == 'restricted':
                    weight: int | float = 2
                elif target_hub.type.value == 'priority':
                    weight = 0.9
                else:
                    weight = 1

                if agent.is_in_flight:
                    # Agent is mid-transit toward a restricted zone
                    agent.move_to_next(weight)
                    turn_moves.append(f"{agent.agent_id}-{display_target}")
                else:
                    self.graph.occupancy[agent.current_hub] -= 1
                    self.graph.occupancy[target_name] += 1

                    if weight > 1:
                        # Show connection segment for restricted transit
                        turn_moves.append(
                            f"{agent.agent_id}-"
                            f"{display_current}-{display_target}"
                        )
                    else:
                        turn_moves.append(
                            f"{agent.agent_id}-{display_target}"
                        )

                    agent.move_to_next(weight)

            if turn_moves:
                print(" ".join(turn_moves))
