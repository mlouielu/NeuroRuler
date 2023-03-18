"""Global variables and functions that the user should not be able to modify directly.

Can run this file as module (python -m src.utils.globs) to test stuff."""

import SimpleITK as sitk
import warnings
import functools
from typing import Union
from numpy import pi
from src.utils.mri_image import MRIImageList, MRIImage
from pathlib import Path

IMAGE_LIST: MRIImageList = MRIImageList()
"""Global list of MRIImage."""
SUPPORTED_EXTENSIONS: tuple = ('*.nii.gz', '*.nii', '*.nrrd')
"""File formats supported. Must be a subset of the file formats supported by SimpleITK."""
EXAMPLE_DATA_DIR: Path = Path.cwd() / 'ExampleData'
"""Directory for storing example data."""
EXAMPLE_IMAGES: list[MRIImage] = []
"""`list[MRIImage]` formed from the data in `EXAMPLE_DATA_DIR`."""
READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""
THEME_DIR: Path = Path.cwd() / 'src' / 'GUI' / 'themes'
THEMES: set[str] = {'dark-hct', 'light-hct', 'dark', 'light'}
APP_MAIN_COLOR: str = "b55162"
"""The pink-ish color used in the midterm presentation."""

for extension in SUPPORTED_EXTENSIONS:
    for path in EXAMPLE_DATA_DIR.glob(extension):
        EXAMPLE_IMAGES.append(MRIImage(path))

NUM_CONTOURS_IN_INVALID_SLICE: int = 10
"""If this number of contours or more is detected in a slice after processing (Otsu, largest component, etc.), then the slice is considered invalid."""

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


def main():
    """For testing."""
    print(EXAMPLE_IMAGES)
    print(f'\nNumber of example images in {str(EXAMPLE_DATA_DIR.name)}/: {len(EXAMPLE_IMAGES)}')
    print(f'img.get_size(): {EXAMPLE_IMAGES[0].get_size()}')
    # Errors for some reason, but the return type of sitk.Image.GetSize() is tuple, tested in terminal
    # print(f'type(img.get_size()): {type(EXAMPLE_IMAGES[0].get_size())}')


if __name__ == "__main__":
    main()
