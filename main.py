import sys
from map_reader import MapReader
from network_graph import NetworkGraph
from engine import Engine


def main() -> None:
    """Entry point — parse the map file and launch the simulation."""
    if len(sys.argv) > 1:

        if sys.argv[1] != "map.txt":
            print("Invalid file: map file must be named 'map.txt'")
            sys.exit(0)

        reader = MapReader()
        reader.parse(sys.argv[1])

        graph = NetworkGraph(reader)

        engine = Engine(graph, int(reader.nb_drones))
        engine.run()

    else:
        print("Usage: python3 main.py map.txt")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
