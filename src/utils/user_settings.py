"""Global settings that the user should be able to modify directly, unlike global_vars.py and constants.py, via
JSON, GUI, CLI, etc.

Default values are what's in the config.json file, which should match what's in this file."""

from pathlib import Path
from screeninfo import get_monitors, ScreenInfoError
import src.utils.constants as constants

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

SMOOTH_BEFORE_RENDERING: bool = False
"""Whether or not to smooth the image before rendering.

Affects img_helpers.curr_rotated_slice() and imgproc.contour()."""

IMG_DIR: Path = Path("img")
"""Directory for storing images. Defaults to `img/`.

TODO: Warn the user that images here may be overwritten in our documentation. It is not a safe directory
to use for file storage and should only be used by the program."""

FILE_BROWSER_START_DIR: Path = Path("ExampleData")
"""The starting directory that is opened in the file browser.

Defaults to ExampleData/ during development, for now.

Should default to the home directory for the user."""


EXPORTED_FILE_NAMES_USE_INDEX: bool = False
"""If True, then exported files will be named using the index in the program.

E.g. 1_0_0_0_0.png, 2_90_180_0_60.csv, etc., where the first part is the file name and
the other parts are image settings.

If False (default), then exported files will be named using the file name of the original file.

E.g. MicroBiome_1month_T1w_0_0_0_0.png, MicroBiome_1month_T1w_90_180_0_60.csv."""

THEME_NAME: str = "dark-hct"
"""Name of theme in src/GUI/themes.

The full path to the .qss file is {constants.THEME_DIR}/{THEME_NAME}/stylesheet.qss."""

CONTOUR_COLOR: str = constants.HCT_MAIN_COLOR
"""Color of the contour. See parser.py for how the default contour color is determined.

This can be a 6-hexit string rrggbb (don't prepend 0x) or a name (e.g. red, blue, etc.).

Internally, this is converted to a QColor using imgproc.string_to_QColor().

QColor supports 8-hexit rrggbbaa but doesn't work in our GUI, i.e. aa=00 appears fully bright in the GUI."""

PRIMARY_MONITOR_DIMENSIONS: list[int] = [500, 500]
"""Set to user's primary monitor's dimensions. 500, 500 are dummy values"""

try:
    for m in get_monitors():
        if m.is_primary:
            PRIMARY_MONITOR_DIMENSIONS[0] = m.width
            PRIMARY_MONITOR_DIMENSIONS[1] = m.height
            break
except ScreenInfoError:
    # This will occur on GH automated tests.
    pass

MIN_WIDTH_RATIO: float = 0.6
"""Min GUI width as fraction of primary monitor width. Configurable in JSON"""
MIN_HEIGHT_RATIO: float = 0.5
"""Min GUI height as fraction of primary monitor height. Configurable in JSON"""
MAX_WIDTH_RATIO: float = 0.6
"""Max GUI width as fraction of primary monitor width. Configurable in JSON"""
MAX_HEIGHT_RATIO: float = 0.6
"""Max GUI height as fraction of primary monitor height. Configurable in JSON"""