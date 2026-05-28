from enum import StrEnum
from pathlib import Path

AVATAR_SIZE = 200
AVATAR_FONT_RATIO = 0.5
AVATAR_TEXT_COLOR = "white"
AVATAR_FONT_PATH = (
    Path(__file__).resolve().parent.parent
    / "static"
    / "fonts"
    / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)


class AvatarColor(StrEnum):
    BLUE = "#4A90D9"
    GREEN = "#5BA85A"
    ORANGE = "#D47A3A"
    PURPLE = "#8B6BB1"
    RED = "#C75B5B"
    TEAL = "#4AADAD"
    AMBER = "#C0934A"
    SLATE = "#7B8CBF"
