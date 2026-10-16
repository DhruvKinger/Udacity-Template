"""Represent models for near-Earth objects (NEOs) and their close approaches.

The `NearEarthObject` class represents a near-Earth object. Each has a
unique primary designation, an optional IAU name, an optional diameter (in
kilometers), and a flag for whether it is potentially hazardous.

The `CloseApproach` class represents a close approach to Earth by an NEO.
Each has an approach datetime, a nominal approach distance (in astronomical
units), and a relative velocity (in kilometers per second).

A `NearEarthObject` maintains a collection of its close approaches, and a
`CloseApproach` maintains a reference to its NEO. The functions that construct
these objects use only the attributes that are relevant to each class; the
two are linked together later by `NEODatabase`.
"""
import math

from helpers import cd_to_datetime, datetime_to_str


class NearEarthObject:
    """A near-Earth object (NEO).

    An NEO encapsulates semantic and physical parameters about the object,
    such as its primary designation (required, unique), IAU name (optional),
    diameter in kilometers (optional - sometimes unknown), and whether it's
    marked as potentially hazardous to Earth.

    A `NearEarthObject` also maintains a collection of its close approaches -
    initialized to an empty collection, but eventually populated in the
    `NEODatabase` constructor.
    """

    def __init__(self, designation, name=None, diameter=None,
                 hazardous=False):
        """Create a new `NearEarthObject`.

        :param designation: The primary designation of this NEO.
        :param name: The IAU name of this NEO. An empty value is stored
            as None.
        :param diameter: The diameter, in kilometers, of this NEO. An empty
            or missing value is stored as NaN.
        :param hazardous: Whether this NEO is potentially hazardous.
        """
        self.designation = str(designation)
        self.name = name if name else None
        if diameter is None or diameter == '':
            self.diameter = float('nan')
        else:
            self.diameter = float(diameter)
        self.hazardous = bool(hazardous)

        # Create an empty initial collection of linked approaches.
        self.approaches = []

    @property
    def fullname(self):
        """Return a representation of the full name of this NEO."""
        if self.name:
            return f'{self.designation} ({self.name})'
        return self.designation

    def serialize(self):
        """Return a dictionary of this NEO's CSV/JSON-ready attributes.

        A missing name is serialized as the empty string, and a missing
        diameter as NaN.
        """
        return {
            'designation': self.designation,
            'name': self.name or '',
            'diameter_km': self.diameter,
            'potentially_hazardous': self.hazardous,
        }

    def __str__(self):
        """Return `str(self)`."""
        hazard = 'is' if self.hazardous else 'is not'
        return (f'NEO {self.fullname} has a diameter of '
                f'{self.diameter:.3f} km and {hazard} potentially hazardous.')

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation."""
        return (f'NearEarthObject(designation={self.designation!r}, '
                f'name={self.name!r}, diameter={self.diameter:.3f}, '
                f'hazardous={self.hazardous!r})')


class CloseApproach:
    """A close approach to Earth by an NEO.

    A `CloseApproach` encapsulates information about the NEO's close approach
    to Earth, such as the date and time (in UTC) of closest approach, the
    nominal approach distance in astronomical units, and the relative velocity
    in kilometers per second.

    A `CloseApproach` also maintains a reference to its `NearEarthObject` -
    initially, this information (the NEO's primary designation) is saved in a
    private attribute, but the referenced NEO is eventually replaced in the
    `NEODatabase` constructor.
    """

    def __init__(self, designation, time, distance=0.0, velocity=0.0):
        """Create a new `CloseApproach`.

        :param designation: The primary designation of the approaching NEO.
        :param time: The approach time, either as a `datetime` or as a
            calendar date string in the NASA format (e.g. "1900-Jan-01 00:11").
        :param distance: The nominal approach distance, in astronomical units.
        :param velocity: The relative velocity, in kilometers per second.
        """
        # The designation is kept privately until the approach is linked to
        # its NEO.
        self._designation = str(designation)
        if isinstance(time, str):
            time = cd_to_datetime(time)
        self.time = time
        self.distance = float(distance)
        self.velocity = float(velocity)

        # Create an attribute for the referenced NEO, originally None.
        self.neo = None

    @property
    def time_str(self):
        """Return a formatted representation of this approach's time.

        The value in `self.time` should be a Python `datetime` object. While a
        `datetime` object has a string representation, the default
        representation includes seconds - significant figures that don't
        exist in our input data set.

        The `datetime_to_str` method converts a `datetime` object to a
        formatted string that can be used in human-readable representations
        and in serialization to CSV and JSON files.
        """
        return datetime_to_str(self.time)

    def serialize(self):
        """Return a dictionary of this approach's CSV/JSON-ready attributes."""
        return {
            'datetime_utc': self.time_str,
            'distance_au': self.distance,
            'velocity_km_s': self.velocity,
        }

    def __str__(self):
        """Return `str(self)`."""
        name = self.neo.fullname if self.neo else self._designation
        return (f"On {self.time_str}, '{name}' approaches Earth at a "
                f'distance of {self.distance:.2f} au and a velocity of '
                f'{self.velocity:.2f} km/s.')

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation."""
        return (f'CloseApproach(time={self.time_str!r}, '
                f'distance={self.distance:.2f}, '
                f'velocity={self.velocity:.2f}, neo={self.neo!r})')