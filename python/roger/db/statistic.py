"""Module providing functions for accessing Statistic table from DB."""

from db.setup import dbClient


def get_statistic():
    """
    Returns the document with Statistic the DataBase table "Statistic"

    Parameters:


    Returns:
    dict: Statistic
    """

    statistic = dbClient['statistic'].find_one()

    return statistic
