"""Defines the `MRIImage` and `MRIImageList` classes.

See https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters.

And https://realpython.com/python-property/.

See https://peps.python.org/pep-0258/#attribute-docstrings for how to document classes to auto-generate documentation."""

import _collections_abc
from typing import Union
import pathlib
import SimpleITK as sitk
import numpy as np
import warnings
import functools
import src.utils.exceptions as exceptions
import src.utils.settings as settings

READER: sitk.ImageFileReader = sitk.ImageFileReader()
ROTATION_MIN: int = 0
"""Degrees"""
ROTATION_MAX: int = 180
"""Degrees"""


# Can't import this from globs due to circular import
# No docstring because no need to document it
# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


# Also can't import from globs. No docstring because no need to document.
def degrees_to_radians(degrees: Union[int, float]) -> float:
    return degrees * np.pi / 180


class MRIImage:
    """Represents an MRI image. Each MRIImage has its own unique sitk.Euler3DTransform, with its own center and rotation values.

    This allows the GUI to remember settings for different MRI images.

    Don't *have* to encapsulate rotation and slice value, but it allows the GUI to remember settings for MRIImages after clicking Next, Previous."""

    def __init__(self, path: pathlib.Path, theta_x: int = 0, theta_y: int = 0, theta_z: int = 0, slice_z: int = 0) -> None:
        """Sets the `base_img` field to be the result of using `sitk` to read `path`.
        
        Initializes a unique `Euler3DTransform` with center and rotation values."""
        self._path = path
        """Path to MRI image. Get, set defined, but set should never be used."""
        self._theta_x = theta_x
        """X rotation value in degrees. Get, set."""
        self._theta_y = theta_y
        """Y rotation value in degrees. Get, set."""
        self._theta_z = theta_z
        """Z rotation value in degrees. Get, set."""
        self._slice_z = slice_z
        """Slice value. Get, set."""
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        """The base image, which should never be mutated. Get."""
        self._euler_3d_transform = sitk.Euler3DTransform()
        """Unique sitk.Euler3DTransform with origin and rotation values. Get."""
        # TODO: This could be the wrong center
        self._euler_3d_transform.SetCenter(self._base_img.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in self._base_img.GetSize()]))
        self._euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(theta_y),
                                             degrees_to_radians(theta_z))

    def __repr__(self) -> str:
        """Prints only the necessary information to identify an `MRIImage`.
        
        That is, ignores `base_img`, `euler_3d_transform`, and `rotated_slice` since those are determined by `path` and rotation and slice values.
        
        But also, those fields can't be represented as `str`.

        :return: str representation of an MRIImage
        :rtype: str"""
        return f'MRIImage(\'{self._path}\', {self._theta_x}, {self._theta_y}, {self._theta_z}, {self._slice_z})'

    # == and != will check reference equality like normal. Use .equals() for deep equality.
    # def __eq__(self, other):
    #     return self.path == other.path and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def equals(self, other) -> bool:
        """Checks for equality. Ignores `base_img` field. If the conditions checked are true, then `base_img` is the same.

        :param other:
        :type other: MRIImage
        :return: True if equal, else False
        :rtype: bool"""
        return self._path == other.path and self._euler_3d_transform.GetCenter() == other.euler_3d_transform.GetCenter() and self._theta_x == other.theta_x and self._theta_y == other.theta_y and self._theta_z == other.theta_z and self._slice_z == other.slice_z

    def deepcopy(self) -> 'MRIImage':
        """Return a deep copy.

        :return: Deep copy
        :rtype: MRIImage"""
        return MRIImage(self._path, self._theta_x, self._theta_y, self._theta_z, self._slice_z)

    @property
    def base_img(self) -> sitk.Image:
        return self._base_img

    @property
    def euler_3d_transform(self) -> sitk.Euler3DTransform:
        return self._euler_3d_transform

    def get_size(self) -> tuple:
        """Returns dimensions of the base image.

        :return: Dimensions
        :rtype: tuple"""
        return self._base_img.GetSize()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def theta_x(self) -> int:
        return self._theta_x

    @property
    def theta_y(self) -> int:
        return self._theta_y

    @property
    def theta_z(self) -> int:
        return self._theta_z

    @property
    def slice_z(self) -> int:
        return self._slice_z

    # No set_img or set_euler_3d_transform functions.

    @path.setter
    def path(self, path: pathlib.Path) -> None:
        """Honestly, this setter should never be called. Just delete the old `MRIImage`, and construct a new one.

        Keeps the same `Euler3DTransform` but sets its center to the center of the new file.
        
        Sets rotation values and slice num to 0 and `resample`s.

        :rtype: None"""
        self._path = path
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        # TODO: This could be the wrong center
        self._euler_3d_transform.SetCenter(self.base_img.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in self.base_img.GetSize()]))
        self._euler_3d_transform.SetRotation(0, 0, 0)
        self._theta_x = 0
        self._theta_y = 0
        self._theta_z = 0
        self._slice_z = 0

    @theta_x.setter
    def theta_x(self, theta_x: int) -> None:
        self._theta_x = theta_x
        self._euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(self._theta_y),
                                             degrees_to_radians(self._theta_z))

    @theta_y.setter
    def theta_y(self, theta_y: int) -> None:
        self._theta_y = theta_y
        self._euler_3d_transform.SetRotation(degrees_to_radians(self._theta_x), degrees_to_radians(theta_y),
                                             degrees_to_radians(self._theta_z))

    @theta_z.setter
    def theta_z(self, theta_z: int) -> None:
        self._theta_z = theta_z
        self._euler_3d_transform.SetRotation(degrees_to_radians(self._theta_x), degrees_to_radians(self._theta_y),
                                             degrees_to_radians(theta_z))

    @slice_z.setter
    def slice_z(self, slice_z: int) -> None:
        self._slice_z = slice_z

    # TODO: Should this apply smoothing first (and remove it from imgproc.py), then return to GUI for display?
    def resample(self) -> sitk.Image:
        """Returns the rotated slice that's the result of resampling with this instance's rotation and slice values.

        The slice is also smoothed if `settings.SMOOTH_BEFORE_RENDERING` is True.

        :return: Rotated slice that's also smoothed if settings.SMOOTH_BEFORE_RENDERING
        :rtype: sitk.Image"""
        rotated_slice: sitk.Image = sitk.Resample(self._base_img, self._euler_3d_transform)[:, :, self._slice_z]
        if settings.SMOOTH_BEFORE_RENDERING:
            smooth_slice: sitk.Image = sitk.GradientAnisotropicDiffusionImageFilter().Execute(
                sitk.Cast(rotated_slice, sitk.sitkFloat64))
            print('resample() returned a smoothed slice')
            return smooth_slice
        return rotated_slice

    # TODO: Should this apply smoothing first (and remove it from imgproc.py), then return to GUI for display?
    def resample_hardcoded(self, theta_x: int = 0, theta_y: int = 0, theta_z: int = 0, slice_z: int = 0) -> sitk.Image:
        """Return the rotated slice with hardcoded settings (i.e., not the instance's settings). Mostly used in test functions.

        Changes the instance's Euler3DTransform's rotation values but resets the values back to original values.

        The slice is also smoothed if `settings.SMOOTH_BEFORE_RENDERING` is True.

        :param theta_x: X rotation value in degrees, defaults to 0
        :type theta_x: int
        :param theta_y: Y rotation value in degrees, defaults to 0
        :type theta_y: int
        :param theta_z: Z rotation value in degrees, defaults to 0
        :type theta_z: int
        :param slice_z: Z slice value, defaults to 0
        :type slice_z: int
        :return: Rotated slice resulting from resampling the base image with the hardcoded values
        :rtype: sitk.Image"""
        self._euler_3d_transform.SetRotation(theta_x, theta_y, theta_z)
        rotated_slice: sitk.Image = sitk.Resample(self._base_img, self._euler_3d_transform)[:, :, slice_z]
        self._euler_3d_transform.SetRotation(self._theta_x, self._theta_y, self._theta_z)
        if settings.SMOOTH_BEFORE_RENDERING:
            smooth_slice: sitk.Image = sitk.GradientAnisotropicDiffusionImageFilter().Execute(
                sitk.Cast(rotated_slice, sitk.sitkFloat64))
            print('resample() returned a smoothed slice')
            return smooth_slice
        return rotated_slice


# Credit: https://github.com/python/cpython/blob/208a7e957b812ad3b3733791845447677a704f3e/Lib/collections/__init__.py#L1174
class MRIImageList(_collections_abc.MutableSequence):
    """Wraps a list[MRIImage] and a single index. Provides methods for moving the index and modifying the list.

    There should only be a single instance of `MRIImageList` since there's a global MRIImageList.
    
    Not enforced, but don't make more than one instance."""

    _index: int = 0
    """Current index. Get, set."""

    def __init__(self, init_list: Union[list[MRIImage], None] = None) -> None:
        self._images = []
        """List of MRIImage. Get, set (but really should never set)."""
        if init_list is not None:
            if type(init_list) == type(self._images):
                self._images[:] = init_list
            elif isinstance(init_list, MRIImageList):
                self._images[:] = init_list.images[:]
            else:
                self._images = init_list

    @property
    def images(self) -> list[MRIImage]:
        return self._images

    @property
    def index(self) -> int:
        return self._index

    @images.setter
    def images(self, images: list[MRIImage]) -> None:
        self._images = images

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    def __repr__(self) -> str:
        """Return `str` representation of `MRIImageList`."""
        return repr(self._images)

    def __len__(self) -> int:
        """Return length of images."""
        return len(self._images)

    def __getitem__(self, i: Union[int, slice]) -> Union[MRIImage, 'MRIImageList']:
        """If `i` is `int`, returns a reference to `self.images[i]`.
        
        If `i` is `slice`, returns a deep copy of the `ImageList`, but the individual elements are shallow copies (i.e., references are the same).
        
        This is the [same behavior as in normal Python](https://stackoverflow.com/questions/19068707/does-a-slicing-operation-give-me-a-deep-or-shallow-copy).

        :param i:
        :type i: int or slice
        :return: Single MRIImage or MRIImageList
        :rtype: MRIImage or MRIImageList"""
        if isinstance(i, slice):
            return self.__class__(self._images[i])
        else:
            return self._images[i]

    # TODO: Make GUI comply with the docstring
    def __delitem__(self, i: int) -> None:
        """TODO: GUI should prevent delete when there's only one image.
        
        If `i == index`, the GUI should re-render the image afterward.

        :param i:
        :type i: int"""
        if len(self) == 0:
            raise exceptions.RemoveFromEmptyList()
        if len(self) == 1:
            raise exceptions.RemoveFromListOfLengthOne()
        del self._images[i]

    # TODO: If i == index, the GUI should re-render the image
    def __setitem__(self, i: int, image: MRIImage) -> None:
        """TODO: If i == index, the GUI should re-render the image
        
        :param i: index
        :type i: int"""
        self._images[i] = image

    def __contains__(self, image: MRIImage) -> bool:
        """:param image:
        :type image: MRIImage"""
        return image in self._images

    # TODO: If i == index, GUI should re-render the image
    def insert(self, i: int, image: MRIImage) -> None:
        """if `i == index`, GUI should re-render the image.
        
        :param i:
        :type i: MRIImage"""
        self._images.insert(i, image)

    def append(self, image: MRIImage) -> None:
        """:param image:
        :type image: MRIImage"""
        self._images.append(image)

    def extend(self, other: Union['MRIImageList', list[MRIImage]]) -> None:
        """Extend images list.

        :param other:
        :type other: list[MRIImage] or MRIImageList"""
        if isinstance(other, MRIImageList):
            self._images.extend(other._images)
        else:
            self._images.extend(other)

    def clear(self) -> None:
        """TODO: If this is called, reset GUI to initial state (i.e., everything disabled).

        Sets _index to 0."""
        self._images.clear()
        self._index = 0

    def pop(self, i: int = -1) -> MRIImage:
        """TODO: GUI should prevent `pop` when there's only one image.
        
        If `i == index`, GUI should re-render image afterward.

        :param i: Defaults to -1 (i.e., pop last element)
        :type i: int
        :return: Popped `MRIImage`
        :rtype: `MRIImage`"""
        if len(self) == 0:
            raise exceptions.RemoveFromEmptyList()
        if len(self) == 1:
            raise exceptions.RemoveFromListOfLengthOne()
        return self._images.pop(i)

    def next(self) -> None:
        """Advance `index` by 1.
        
        If `index` is the last index, wraps to 0.
        
        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index + 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print("Calling next() when the list has one element doesn't do anything.")

    def previous(self) -> None:
        """Decrement `index` by 1.
        
        If `index` is 0, wraps to the last index.

        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index - 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print("Calling previous() when the list has one element doesn't do anything.")
