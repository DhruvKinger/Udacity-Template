"""Extract data on near-Earth objects and close approaches from CSV and JSON.

The `load_neos` function extracts NEO data from a CSV file, formatted as
described in the project instructions, into a collection of
`NearEarthObject`s.

The `load_approaches` function extracts close approach data from a JSON file,
formatted as described in the project instructions, into a collection of
`CloseApproach` instances.

The main module calls these functions with the arguments provided at the
command line, and uses the resulting collections to build an `NEODatabase`.
"""
import csv
import json

from models import NearEarthObject, CloseApproach


def load_neos(neo_csv_path):
    """Read near-Earth object information from a CSV file.

    :param neo_csv_path: A path to a CSV file containing data about
        near-Earth objects.
    :return: A collection of `NearEarthObject`s.
    """
    neos = []
    with open(neo_csv_path, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            neos.append(NearEarthObject(
                designation=row['pdes'],
                name=row['name'],
                diameter=row['diameter'],
                hazardous=row['pha'] == 'Y',
            ))
    return neos


def load_approaches(cad_json_path):
    """Read close approach data from a JSON file.

    :param cad_json_path: A path to a JSON file containing data about close
        approaches.
    :return: A collection of `CloseApproach`es.
    """
    with open(cad_json_path, 'r') as infile:
        contents = json.load(infile)

    # Rely on the "fields" key to locate each value of interest.
    index = {field: i for i, field in enumerate(contents['fields'])}
    return [
        CloseApproach(
            designation=row[index['des']],
            time=row[index['cd']],
            distance=row[index['dist']],
            velocity=row[index['v_rel']],
        )
        for row in contents['data']
    ]