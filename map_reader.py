import re
from models import HubModel, ConnectionModel
from pydantic import ValidationError
import sys
from typing import Dict, List, Any


class MapReader:
    """Reads and validates a network map file, extracting all zones."""

    DRONE_PATTERN = re.compile(r"^nb_drones:\s+(?P<count>[+-]?\d+)$")

    HUB_PATTERN = re.compile(
        r"^\s*"
        r"(?P<type>start_hub|end_hub|hub):"
        r"\s+"
        r"(?P<name>\S+)"
        r"\s+"
        r"(?P<x>[+-]?\d+)"
        r"\s+"
        r"(?P<y>[+-]?\d+)"
        r"(?:\s+\[(?P<meta>.*\S.*)\])?$"
    )

    CONN_PATTERN = re.compile(
        r"^connection:\s+"
        r"(?P<hub_a>\S+)"
        r"-"
        r"(?P<hub_b>\S+)"
        r"(?:\s+\[(?P<meta>.*\S.*)\])?$"
    )

    def __init__(self) -> None:
        """Initialize internal storage for parsed map data."""
        self.hubs: Dict[str, HubModel] = {}
        self.connections: List[ConnectionModel] = []
        self.nb_drones: str | Any = None
        self.valid_hub_meta = ['color', 'zone', 'max_drones', 'cost']
        self.valid_conn_meta = ['max_link_capacity']
        self.start: str | Any = None
        self.end: str | Any = None

    def _clean_line(self, line: str) -> str | Any:
        """Strip inline comments and surrounding whitespace from a raw line.

        Args:
            line: The raw line string from the file.

        Returns:
            Cleaned line string without comment content.
        """
        if '#' in line:
            trimmed = ""
            for ch in line:
                if ch == '#':
                    break
                trimmed += ch
            return trimmed
        return line

    def _parse_metadata(self, meta_str: str, line_num: int) -> Dict[str, str]:
        """Parse a metadata block string into a key-value dictionary.

        Args:
            meta_str: Raw metadata string from inside brackets.
            line_num: Line number for error reporting.

        Returns:
            Dictionary of parsed key-value pairs.

        Raises:
            ValueError: If a metadata component is malformed.
        """
        if not meta_str:
            return {}

        parts = meta_str.strip().split()
        metadata: Dict[str, str] = {}
        pair_re = re.compile(r"^(?P<key>\w+)=(?P<value>[+-]?[\w-]+)$")

        for part in parts:
            match = pair_re.match(part)
            if not match:
                raise ValueError(
                    f"Line {line_num}: Malformed metadata '{part}'. "
                    "Expected format: [key=value ...]"
                )
            metadata[match.group("key")] = match.group("value")

        return metadata

    def parse(self, file_path: str) -> None:
        """Open and process the map file line by line.

        Args:
            file_path: Path to the .txt map file to read.

        Raises:
            ValueError: On any structural or semantic parsing error.
        """
        with open(file_path, 'r') as f:
            has_content = False

            for line_num, raw_line in enumerate(f, start=1):
                has_content = True
                cleaned = self._clean_line(raw_line).strip()

                if not cleaned or cleaned.startswith('#'):
                    continue

                # ── nb_drones must be first valid line ──────────────────
                if self.nb_drones is None:
                    match = self.DRONE_PATTERN.match(cleaned)
                    if match:
                        count = int(match.group("count"))
                        if count < 1:
                            raise ValueError(
                                f"Line {line_num}: 'nb_drones' must be >= 1."
                            )
                        self.nb_drones = count
                        continue
                    else:
                        raise ValueError(
                            f"Line {line_num}: First valid line must define "
                            "'nb_drones: <int>'"
                        )

                # ── Hub / zone definitions ──────────────────────────────
                if cleaned.startswith(("hub:", "start_hub:", "end_hub:")):
                    hub_match = self.HUB_PATTERN.match(cleaned)

                    if not hub_match:
                        raise ValueError(
                            f"Line {line_num}: Malformed hub definition. "
                            "Expected: 'type: name x y [meta]'"
                        )

                    data = hub_match.groupdict()

                    if data['meta'] == "":
                        raise ValueError(
                            f"Line {line_num}: Meta block empty."
                        )

                    raw_type = data['type']

                    # Enforce uniqueness of start and end hubs
                    if raw_type == 'start_hub':
                        if self.start:
                            raise ValueError(
                                f"Line {line_num}: Start hub exists."
                            )
                        self.start = data['name']

                    if raw_type == 'end_hub':
                        if self.end:
                            raise ValueError(
                                f"Line {line_num}: End hub exists."
                            )
                        self.end = data['name']

                    if data['name'] in self.hubs:
                        raise ValueError(
                            f"Line {line_num}: Duplicate zone name "
                            f"'{data['name']}'."
                        )

                    meta = self._parse_metadata(data.pop('meta'), line_num)
                    # if raw_type == 'start_hub' and meta['zone'] == 'blocked':
                    #     raise ValueError(f"Line {line_num}: start cannot be "
                    #                      "blocked")
                    # elif raw_type == 'end_hub' and meta['zone'] == 'blocked':
                    #     raise ValueError(f"Line {line_num}: end cannot be "
                    #                      "blocked")
                    has_explicit_cost = 'cost' in meta
                    if not has_explicit_cost:
                        meta['cost'] = '1'

                    for key, value in list(meta.items()):
                        if key not in self.valid_hub_meta:
                            raise ValueError(
                                f"Line {line_num}: Unknown meta key '{key}'. "
                                f"Valid keys: {self.valid_hub_meta}"
                            )
                        if key == 'color':
                            pass
                        if key == 'zone' and not has_explicit_cost:
                            if value == 'restricted':
                                meta['cost'] = '2'
                            elif value == 'priority':
                                meta['cost'] = '1'

                    data.pop('type')

                    if 'zone' in meta:
                        data['type'] = meta.pop('zone')

                    data.update(meta)
                    if raw_type == "start_hub":
                        if data.get('type', "") == "blocked":
                            raise ValueError(f"Line {line_num}: start cannot"
                                             " be blocked")
                    elif raw_type == "end_hub":
                        if data.get('type', "") == "blocked":
                            raise ValueError(f"Line {line_num}: end cannot"
                                             " be blocked")
                    if raw_type in ["start_hub", "end_hub"]:
                        data['max_drones'] = self.nb_drones

                    try:
                        new_hub = HubModel.model_validate(data)

                        for existing_hub in self.hubs.values():
                            if (existing_hub.x == new_hub.x and
                                    existing_hub.y == new_hub.y):
                                raise ValueError(
                                    f"Line {line_num}: Duplicate coordinates "
                                    f"({new_hub.x}, {new_hub.y}) for zone "
                                    f"'{new_hub.name}', already used by "
                                    f"'{existing_hub.name}'."
                                )

                        self.hubs[new_hub.name] = new_hub

                    except ValidationError as e:
                        for err in e.errors():
                            if 'Value error' in err['msg']:
                                parts = err['msg'].split(',')
                                print(f"Line {line_num}:", parts[1].strip())
                            else:
                                print(f"Line {line_num}:", err['msg'])
                            sys.exit(1)

                    continue

                # ── Connection definitions ──────────────────────────────
                if cleaned.startswith("connection:"):
                    conn_match = self.CONN_PATTERN.match(cleaned)

                    if not conn_match:
                        raise ValueError(
                            f"Line {line_num}: Malformed connection. "
                            "Expected: 'connection: zoneA-zoneB [meta]'"
                        )

                    data = conn_match.groupdict()

                    if data['meta'] == "":
                        raise ValueError(
                            f"Line {line_num}: Meta block empty."
                        )

                    meta = self._parse_metadata(data.pop('meta'), line_num)

                    for key in meta:
                        if key not in self.valid_conn_meta:
                            raise ValueError(
                                f"Line {line_num}: Unknown meta key '{key}'. "
                                f"Valid keys: {self.valid_conn_meta}"
                            )

                    data.update(meta)

                    try:
                        if data['hub_a'] not in self.hubs:
                            raise ValueError(
                                f"'{data['hub_a']}' is not a defined zone."
                            )
                        if data['hub_b'] not in self.hubs:
                            raise ValueError(
                                f"'{data['hub_b']}' is not a defined zone."
                            )

                        new_conn = ConnectionModel.model_validate(data)

                        if new_conn in self.connections:
                            raise ValueError(
                                f"Duplicate connection "
                                f"'{new_conn.hub_a}-{new_conn.hub_b}'."
                            )

                        self.connections.append(new_conn)

                    except ValidationError as e:
                        for err in e.errors():
                            if 'Value error' in err['msg']:
                                parts = err['msg'].split(',')
                                print(f"Line {line_num}:", parts[1].strip())
                            else:
                                print(f"Line {line_num}:", err['msg'])
                            sys.exit(1)
                    except ValueError as e:
                        print(f"Line {line_num}: {e}")
                        sys.exit(1)

                    continue

                raise ValueError(
                    f"Line {line_num}: Unrecognized syntax.\n"
                    f"Invalid line: [{cleaned}]"
                )

            if not has_content:
                raise ValueError("Map file is empty.")
            if not self.start:
                raise ValueError("No 'start_hub' defined in map.")
            if not self.end:
                raise ValueError("No 'end_hub' defined in map.")
