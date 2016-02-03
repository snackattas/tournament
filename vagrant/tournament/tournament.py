#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection, and the cursor."""
    database = psycopg2.connect("dbname=tournament")
    cursor = database.cursor()
    return (database, cursor)


def deleteMatches():
    (database, cursor) = connect()
    cursor.execute("DELETE FROM matches;")
    database.commit()
    database.close()
    return ""

def deletePlayers():
    """Remove all the player records from the database."""
    (database, cursor) = connect()
    cursor = database.cursor()
    cursor.execute("DELETE FROM players;")
    database.commit()
    database.close()
    return ""

def countPlayers():
    """Returns the number of players currently registered."""
    (database, cursor) = connect()
    cursor.execute("SELECT count(*) from players;")
    no_of_players = cursor.fetchall()
    database.close()
    return int(no_of_players[0][0])

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    (database, cursor) = connect()
    cursor.execute("INSERT INTO players VALUES (DEFAULT, %s)", (name, ))
    database.commit()
    database.close()
    return ""

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """


def reportMatch(winner, loser, tie = False):
    """Records the outcome of a single match between two players. User must pass
    in values for winner and loser. tie is optional.

    Args:
      winner:  the id number of the player who won.
      loser:  the id number of the player who lost.
      tie (DEFAULT = FALSE): pass in TRUE if the players tied.  In this case,
                             the columns for winner and loser don't represent
                             the actual winner/loser.  They represent the
                             participants.
    """

    if not winner and loser:
        raise ValueError("user must pass in both a winner and loser to "
                        "reportMatch")

    (database, cursor) = connect()
    cursor.execute("INSERT INTO matches VALUES (DEFAULT, %s, %s, %s)",
                  (winner, loser, tie,))
    database.commit()
    database.close()
    return ""

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
def populate(m):
    for n in range(m):
        registerPlayer("zachy"+str(n+1))
def rmtest():
    reportMatch(1,2)
    reportMatch(4,3)
    reportMatch(5,6)
    reportMatch(8,7)
    reportMatch(9,10,True)
    reportMatch(11,12,True)
    reportMatch(9,13)
    reportMatch(13,9)
    reportMatch(1,10,True)
    return ""
