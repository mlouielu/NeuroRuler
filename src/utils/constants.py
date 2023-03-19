"""Constant values and functions.

Some of this stuff used to be in `globs.py`. However, globs imports from src.utils.mri_image, which
creates circular imports.

This file should never import any module in this repo to avoid any circular import problems.

It should hold values that will never change after program setup and during execution, unlike globs.py.
But things like THEMES can go here. Specifically, THEMES is a mutable set, but it should never
change after initial setup.

No values here should be modifiable by the user, unlike settings.py."""

from pathlib import Path
import warnings
import functools
from numpy import pi
from typing import Union

ROTATION_MIN: int = -90
"""In degrees"""
ROTATION_MAX: int = 90
"""In degrees"""

SUPPORTED_EXTENSIONS: tuple = ('*.nii.gz', '*.nii', '*.nrrd')
"""File formats supported. Must be a subset of the file formats supported by SimpleITK."""
EXAMPLE_DATA_DIR: Path = Path('ExampleData')
"""Directory for storing example data."""

THEME_DIR: Path = Path('src') / 'GUI' / 'themes'
"""themes/ directory where .qss stylesheets and resources.py files are stored."""
THEMES: set[str] = set()
"""List of themes, i.e. the names of the directories in THEME_DIR."""
if len(list(THEME_DIR.glob('*'))) != 0:
    for path in THEME_DIR.iterdir():
        if path.is_dir():
            THEMES.add(path.name)
else:
    # TODO: Without this, autodocumentation will crash. Is there a better way around this?
    print(f'No themes discovered in {str(THEME_DIR)}. Make sure to run from .../HeadCircumferenceTool .')

APP_MAIN_COLOR: str = "b55162"
"""The pink-ish color used in the midterm presentation."""

NUM_CONTOURS_IN_INVALID_SLICE: int = 10
"""If this number of contours or more is detected in a slice after processing (Otsu, largest component, etc.),
then the slice is considered invalid."""

NIFTI_UNITS = {
    '0': 'Unknown',
    '1': 'Meter (m)',
    '2': 'Millimeter (mm)',
    '3': 'Micron (μm)',
    '8': 'Seconds (s)',
    '16': 'Milliseconds (ms)',
    '24': 'Microseconds (μs)',
    '32': 'Hertz (Hz)',
    '40': 'Parts-per-million (ppm)',
    '48': 'Radians per second (rad/s)'
}
"""Maps the `xyzt_units` metadata field of a NIfTI file to physical meaning.

Based on https://brainder.org/2012/09/23/the-nifti-file-format/.

See the top of Playground/imgproc/processing.ipynb for `sitk` code to get metadata."""


# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def degrees_to_radians(angle: Union[int, float]) -> float:
    """:param num: A degree measure
    :type num: int or float
    :return: Equivalent radian measure
    :rtype: float"""
    return angle * pi / 180
