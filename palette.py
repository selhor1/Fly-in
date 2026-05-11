class TerminalPalette:
    """Holds all ANSI escape codes for terminal coloring throughout the simulation."""

    colors = {
        "reset":   '\033[0m',
        "black":   '\033[30m',
        "red":     '\033[91m',
        "green":   '\033[92m',
        "yellow":  '\033[93m',
        "blue":    '\033[94m',
        "magenta": '\033[95m',
        "cyan":    '\033[96m',
        "white":   '\033[97m',
        "gray":    '\033[90m',
        "brown":   '\033[38;5;130m',
        "pink":    '\033[38;5;206m',
        "orange":  '\033[38;5;208m',
        "purple":  '\033[38;5;129m',
        "maroon":  '\033[38;5;52m',
        "gold":    '\033[38;5;220m',
        "darkred": '\033[38;5;88m',
        "violet":  '\033[38;5;135m',
        "crimson": '\033[38;5;161m',
        "lime":    '\033[38;5;118m'
    }

    def apply_rainbow(self, text: str) -> str:
        """Apply a rainbow gradient effect character by character to a string."""
        gradient = [
            self.colors["red"],    self.colors["orange"], self.colors["yellow"],
            self.colors["green"],  self.colors["blue"],   self.colors["purple"],
            self.colors["violet"]
        ]
        result = ""
        for index, char in enumerate(text):
            chosen = gradient[index % len(gradient)]
            result += f"{chosen}{char}"
        return result + self.colors["reset"]

    def colorize(self, text: str, color_name: str) -> str:
        """Wrap a string with the given color code and reset."""
        if color_name == "rainbow":
            return self.apply_rainbow(text)
        code = self.colors.get(color_name, "")
        if code:
            return f"{code}{text}{self.colors['reset']}"
        return text
