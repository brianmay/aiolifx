""" Define colours for use with aiolifxc. """
from typing import Tuple

UINT16_MAX = pow(2, 16) - 1

HUE_MAX = 360
KELVIN_MIN = 2500
KELVIN_MAX = 9000
KELVIN_RANGE = KELVIN_MAX - KELVIN_MIN

MID_KELVIN = int(KELVIN_MIN + (KELVIN_RANGE/2))


class Color:
    """ An immutable type representing a colour. """
    def __init__(self, hue: int, saturation: int, brightness: int, kelvin: int) -> None:
        """
        Create a new colour using HSBK.

        :param hue: Range 0 to 360.
        :param saturation: Range 0 to 100.
        :param brightness: Range 0 to 100.
        :param kelvin: Range 2500 to 9000.
        """
        self._hue = hue
        self._saturation = saturation
        self._brightness = brightness
        self._kelvin = kelvin

    def clone(self) -> 'Color':
        return type(self)(self._hue, self._saturation, self._brightness, self._kelvin)

    def get_values(self) -> Tuple[int, int, int, int]:
        return (
            int(self._hue / HUE_MAX * UINT16_MAX),
            int(self._saturation / 100 * UINT16_MAX),
            int(self._brightness / 100 * UINT16_MAX),
            self._kelvin,
        )

    @classmethod
    def create_from_values(cls, values: Tuple[int, int, int, int]) -> 'Color':
        return cls(
            hue=int(values[0] / UINT16_MAX * HUE_MAX),
            saturation=int(values[1] / UINT16_MAX * 100),
            brightness=int(values[2] / UINT16_MAX * 100),
            kelvin=values[3],
        )

    def __str__(self) -> str:
        return "Colour: %d %d %d %d" % (
            self._hue, self._saturation, self._brightness, self._kelvin)


# Bright Colors
RED = Color(0, 100, 100, MID_KELVIN)
YELLOW = Color(60, 100, 100, MID_KELVIN)
GREEN = Color(120, 100, 100, MID_KELVIN)
AQUA = Color(180, 100, 100, MID_KELVIN)
BLUE = Color(240, 100, 100, MID_KELVIN)
PURPLE = Color(300, 100, 100, MID_KELVIN)
WHITE = Color(0, 0, 100, MID_KELVIN)

# Whites
COOL_WHITE = Color(0, 0, 100, KELVIN_MAX)
WARM_WHITE = Color(0, 0, 100, KELVIN_MIN)
