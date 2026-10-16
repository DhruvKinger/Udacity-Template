"""A database encapsulating collections of near-Earth objects and approaches.

A `NEODatabase` holds an interconnected data set of NEOs and close approaches.
It provides methods to fetch an NEO by primary designation or by name, as well
as a method to query the set of approaches that match a collection of
user-specified criteria.

Under the hood, it maintains a collection of NEOs and a collection of close
approaches, along with dictionaries that speed up lookups by designation
and name.
"""


class NEODatabase:
    """A database of near-Earth objects and their close approaches.

    A `NEODatabase` contains a collection of NEOs and a collection of close
    approaches. It additionally maintains auxiliary data structures to help
    fetch NEOs by primary designation or by name and to help speed up
    querying for close approaches that match criteria.
    """

    def __init__(self, neos, approaches):
        """Create a new `NEODatabase`.

        As a precondition, this constructor assumes that the collections of
        NEOs and close approaches aren't change, and that the data is
        well-formatted: no NEO has a duplicate primary designation, and
        every close approach refers to an NEO that is in the collection.

        The constructor links every approach to its NEO (via the `neo`
        attribute) and populates every NEO's `approaches` collection.

        :param neos: A collection of `NearEarthObject`s.
        :param approaches: A collection of `CloseApproach`es.
        """
        self._neos = neos
        self._approaches = approaches

        # Dictionaries that make lookups by designation or name O(1). Only
        # real (nonempty) names are ever used as keys.
        self._neos_by_designation = {
            neo.designation: neo for neo in self._neos
        }
        self._neos_by_name = {
            neo.name: neo for neo in self._neos if neo.name
        }

        # Link each close approach to its NEO, and vice versa.
        for approach in self._approaches:
            neo = self._neos_by_designation.get(approach._designation)
            if neo is not None:
                approach.neo = neo
                neo.approaches.append(approach)

    def get_neo_by_designation(self, designation):
        """Find and return an NEO by its primary designation.

        If no match is found, return `None` instead.

        Each NEO in the data set has a unique primary designation, as a
        string.

        :param designation: The primary designation of the NEO to search for.
        :return: The `NearEarthObject` with the desired primary designation,
            or `None`.
        """
        return self._neos_by_designation.get(designation)

    def get_neo_by_name(self, name):
        """Find and return an NEO by its name.

        If no match is found, return `None` instead.

        Not every NEO in the data set has a name. No NEOs are associated with
        the empty string nor with the `None` singleton. If several NEOs share
        a name, any one of them may be returned.

        :param name: The name, as a string, of the NEO to search for.
        :return: The `NearEarthObject` with the desired name, or `None`.
        """
        return self._neos_by_name.get(name)

    def query(self, filters=()):
        """Query close approaches to generate those that match a collection
        of filters.

        This generates a stream of `CloseApproach` objects that match all of
        the provided filters, without precomputing the full result set.

        If no arguments are provided, generate all known close approaches.

        :param filters: A collection of filters (callables) that each accept
            a `CloseApproach` and return a boolean.
        :return: A stream of matching `CloseApproach` objects.
        """
        filters = filters or ()
        for approach in self._approaches:
            if all(approach_filter(approach)
                   for approach_filter in filters):
                yield approach