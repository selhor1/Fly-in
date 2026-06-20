*This project has been created as part of the 42 curriculum by selhor.*

# Fly-in: Autonomous Drone Routing System

## Description
Fly-in is a multi-agent drone routing simulation designed to navigate a fleet of drones through a complex network of zones. The goal is to deliver all drones from a starting hub to a destination hub in the minimum number of simulation turns while respecting movement constraints, zone capacities, and connection limits.

The system handles different zone types:
- **Normal:** 1 turn movement cost.
- **Priority:** 1 turn cost, but preferred by the pathfinder.
- **Restricted:** 2 turn cost (requires a transit turn on the connection).
- **Blocked:** Inaccessible.

## Instructions

### Installation
The project requires Python 3.10+ and the Pydantic library. It is recommended to use the provided Makefile to set up a virtual environment.

```bash
make venv
source drone_env/bin/activate
make install
```

### Execution
Run the simulation by providing a map file:

```bash
make run MAP=map.txt
```

### Development & Linting
To ensure code quality and type safety:

```bash
make lint
```

## Technical Choices & Algorithm

### Pathfinding: Space-Time Dijkstra
The core of Fly-in is a **Space-Time Dijkstra** algorithm. Unlike standard pathfinding, this algorithm treats "Time" as a third dimension. This allows drones to:
1.  **Predict the future:** Drones "book" time slots in hubs and connections.
2.  **Avoid Collisions:** A drone will only choose a path if the destination zone and the link are available at the specific turn it arrives.
3.  **Wait Strategically:** If all paths are blocked, a drone can "move" to its current location (wait-in-place) to wait for a slot to open up.

### Algorithm Strategy
- **Greedy Scheduling:** Drones are routed one by one. Each drone reserves its entire path in a `SlotManager` before the next drone's path is calculated.
- **Priority Handling:** Zones marked as `priority` have a standard cost of 1 but are preferred by the pathfinder when determining routes of equal length, encouraging the pathfinder to utilize them to reduce overall congestion.
- **Restricted Transit:** The engine specifically manages 2-turn movements by tracking "in-flight" states, ensuring drones occupy the link during transit turns.

## Visual Representation
The simulation provides rich terminal feedback:
- **Simulation Overview:** A detailed breakdown of the network topology, zone types, and capacities is printed before the simulation starts.
- **Color-Coded Output:** Hubs are colorized in the terminal based on their metadata (e.g., green for start, yellow for end, red for restricted).
- **Movement Logs:** Every turn, the system outputs the current position of all moving drones, including those in transit between hubs.

## Resources
- **Dijkstra's Algorithm:** Standard weighted shortest path.
- **Multi-Agent Pathfinding (MAPF):** Research on collision-free routing.
- **AI Usage:** AI was used to assist in designing the Pydantic data models for the parser and for refining the space-time reservation logic to ensure strict adherence to the subject's turn mechanics.
