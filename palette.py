import matplotlib.colors as mcolors


class TerminalPalette:
    """Holds all ANSI escape codes for terminal coloring."""

    COLORS = {
        "reset": "\033[0m",
    }

    def colorize(self, text: str, color_name: str) -> str:
        """Apply ANSI color codes to a string.

        Args:
            text: The string to colorize.
            color_name: Any valid matplotlib CSS4 color or 'rainbow'.

        Returns:
            The colorized string.
        """
        color_lower = color_name.lower()

        if color_lower == 'rainbow':
            rainbow_colors = [
                'red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'
            ]
            result = ""
            for i, char in enumerate(text):
                color = rainbow_colors[i % len(rainbow_colors)]
                r, g, b = mcolors.to_rgb(mcolors.CSS4_COLORS[color])
                r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
                color_code = f"\033[38;2;{r_int};{g_int};{b_int}m"
                result += f"{color_code}{char}"
            return f"{result}{self.COLORS['reset']}"

        try:
            if color_lower in mcolors.CSS4_COLORS:
                css_hex = mcolors.CSS4_COLORS[color_lower]
                r, g, b = mcolors.to_rgb(css_hex)
            else:
                r, g, b = mcolors.to_rgb(color_name)

            r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
            color_code = f"\033[38;2;{r_int};{g_int};{b_int}m"
            return f"{color_code}{text}{self.COLORS['reset']}"
        except ValueError:
            return text
