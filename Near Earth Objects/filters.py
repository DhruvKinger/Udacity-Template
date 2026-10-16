"""Provide filters for querying close approaches and limit the generated
results.

The `create_filters` function produces a collection of objects that is used by
the `query` method to generate a stream of `CloseApproach` objects that match
all of the desired criteria. The arguments to `create_filters` are provided by
the main module and originate from the user's command-line options.

The `limit` function limits the number of values produced by an iterator,
without buffering the iterator into memory.
"""
import itertools
import operator


class UnsupportedCriterionError(NotImplementedError):
    """A filter criterion is unsupported."""


class AttributeFilter:
    """A general superclass for filters on comparable attributes.

    An `AttributeFilter` represents the search criteria pattern comparing some
    attribute of a close approach (or its attached NEO) to a reference value.
    It essentially functions as a callable predicate for whether a
    `CloseApproach` object satisfies the encoded criterion.

    It is constructed with a comparator operator and a reference value, and
    calling the filter (with __call__) executes `get(approach) OP value` (in
    infix notation).

    Concrete subclasses can override the `get` classmethod to provide custom
    behavior to fetch a desired attribute from the given `CloseApproach`.
    """

    def __init__(self, op, value):
        """Construct a new `AttributeFilter` from an binary predicate and a
        reference value.

        The reference value will be supplied as the second (right-hand side)
        argument to the operator function. For example, an `AttributeFilter`
        with `op=operator.le` and `value=10` will, when called on an approach,
        evaluate `some_attribute <= 10`.

        :param op: A 2-argument predicate comparator (such as `operator.le`).
        :param value: The reference value to compare against.
        """
        self.op = op
        self.value = value

    def __call__(self, approach):
        """Invoke `self(approach)`."""
        return self.op(self.get(approach), self.value)

    @classmethod
    def get(cls, approach):
        """Get an attribute of interest from a close approach.

        Concrete subclasses must override this method to get an attribute of
        interest from the supplied `CloseApproach`.

        :param approach: A `CloseApproach` on which to evaluate this filter.
        :return: The value of an attribute of interest, comparable to
            `self.value` via `self.op`.
        """
        raise UnsupportedCriterionError

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation."""
        return (f'{self.__class__.__name__}'
                f'(op=operator.{self.op.__name__}, value={self.value})')


class DateFilter(AttributeFilter):
    """Filter close approaches by the calendar date of the approach."""

    @classmethod
    def get(cls, approach):
        """Return the date (not datetime) of the approach."""
        return approach.time.date()


class DistanceFilter(AttributeFilter):
    """Filter close approaches by nominal approach distance."""

    @classmethod
    def get(cls, approach):
        """Return the approach distance, in astronomical units."""
        return approach.distance


class VelocityFilter(AttributeFilter):
    """Filter close approaches by relative velocity."""

    @classmethod
    def get(cls, approach):
        """Return the relative velocity, in kilometers per second."""
        return approach.velocity


class DiameterFilter(AttributeFilter):
    """Filter close approaches by the diameter of the approaching NEO."""

    @classmethod
    def get(cls, approach):
        """Return the NEO's diameter, in kilometers (NaN if unknown)."""
        return approach.neo.diameter


class HazardousFilter(AttributeFilter):
    """Filter close approaches by whether the NEO is potentially hazardous."""

    @classmethod
    def get(cls, approach):
        """Return whether the approaching NEO is potentially hazardous."""
        return approach.neo.hazardous


def create_filters(
        date=None, start_date=None, end_date=None,
        distance_min=None, distance_max=None,
        velocity_min=None, velocity_max=None,
        diameter_min=None, diameter_max=None,
        hazardous=None
):
    """Create a collection of filters from user-specified criteria.

    Each of these arguments is provided by the main module with a value from
    the user's options at the command line. Each one corresponds to a
    different type of filter. For example, the `--date` option corresponds to
    the `date` argument, and represents a filter that selects close approaches
    that occurred on exactly that given date. Similarly, the `--min-distance`
    option corresponds to the `distance_min` argument, and represents a filter
    that selects close approaches whose nominal approach distance is at least
    that far away from Earth. Each option is `None` if not specified at the
    command line (in particular, `hazardous` is `None` unless either
    `--hazardous` or `--not-hazardous` is given, and is `False` for
    `--not-hazardous`).

    The return value must be compatible with the `query` method of
    `NEODatabase` because the main module directly passes this result to that
    method. For now, this can be thought of as a collection of
    `AttributeFilter`s.

    :param date: A `date` on which a matching `CloseApproach` occurs.
    :param start_date: A `date` on or after which a matching `CloseApproach`
        occurs.
    :param end_date: A `date` on or before which a matching `CloseApproach`
        occurs.
    :param distance_min: A minimum nominal approach distance (au).
    :param distance_max: A maximum nominal approach distance (au).
    :param velocity_min: A minimum relative approach velocity (km/s).
    :param velocity_max: A maximum relative approach velocity (km/s).
    :param diameter_min: A minimum NEO diameter (km).
    :param diameter_max: A maximum NEO diameter (km).
    :param hazardous: Whether the NEO of a matching `CloseApproach` is
        potentially hazardous.
    :return: A collection of filters for use with `query`.
    """
    criteria = (
        (DateFilter, operator.eq, date),
        (DateFilter, operator.ge, start_date),
        (DateFilter, operator.le, end_date),
        (DistanceFilter, operator.ge, distance_min),
        (DistanceFilter, operator.le, distance_max),
        (VelocityFilter, operator.ge, velocity_min),
        (VelocityFilter, operator.le, velocity_max),
        (DiameterFilter, operator.ge, diameter_min),
        (DiameterFilter, operator.le, diameter_max),
        (HazardousFilter, operator.eq, hazardous),
    )
    # Compare against None explicitly: `hazardous=False` and a distance of
    # 0 are legitimate, specified values.
    return tuple(
        filter_class(op, value)
        for filter_class, op, value in criteria
        if value is not None
    )


def limit(iterator, n=None):
    """Produce a limited stream of values from an iterator.

    If `n` is 0 or None, don't limit the iterator at all.

    :param iterator: An iterator of values.
    :param n: The maximum number of values to produce.
    :yield: The first (at most) `n` values from the iterator.
    """
    if not n:
        return iter(iterator)
    return itertools.islice(iterator, n)