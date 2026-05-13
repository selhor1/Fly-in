class TerminalPalette:
    """Holds all ANSI escape codes for terminal coloring."""

    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "reset": "\033[0m",
    }

    def get_agent_color(self, agent_id: str) -> str:
        """Assign a consistent color to a drone ID based on its number.

        Args:
            agent_id: The ID of the drone (e.g., 'D1').

        Returns:
            The color name.
        """
        # Cycle through magenta, cyan, yellow, blue, red
        colors = ["magenta", "cyan", "yellow", "blue", "red"]
        try:
            # Extract number from ID like 'D1'
            idx = int(agent_id[1:]) - 1
            return colors[idx % len(colors)]
        except (ValueError, IndexError):
            return "white"

    def colorize(self, text: str, color_name: str) -> str:
        """Apply ANSI color codes to a string.

        Args:
            text: The string to colorize.
            color_name: The key in COLORS to use.

        Returns:
            The colorized string.
        """
        color_code = self.COLORS.get(color_name.lower(), self.COLORS["reset"])
        return f"{color_code}{text}{self.COLORS['reset']}"
