import psycopg2
import bleach
from operator import itemgetter


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection, and the cursor."""
    database = psycopg2.connect("dbname=tournament")
    cursor = database.cursor()
    return (database, cursor)

def deleteTournament(tournament_id):
    (database, cursor) = connect()
    cursor.execute("DELETE FROM records WHERE tournament_id = %s; DELETE FROM matchRegistry WHERE tournament_id = %s; DELETE FROM players WHERE tournament_id = %s; DELETE FROM tournaments WHERE tournament_id = %s", (tournament_id,tournament_id,tournament_id,tournament_id,))
    database.commit()
    database.close()

def deleteMatches(tournament_id = 1):
    (database, cursor) = connect()
    cursor.execute("DELETE FROM records WHERE tournament_id = %s; DELETE FROM matchRegistry WHERE tournament_id = %s;", (tournament_id, tournament_id,))
    database.commit()
    database.close()

def deletePlayers(tournament_id = 1):
    """Remove all the player records from the database."""
    (database, cursor) = connect()
    cursor = database.cursor()
    cursor.execute("DELETE FROM players WHERE tournament_id = %s;", (tournament_id,))
    database.commit()
    database.close()


def countPlayers(tournament_id = 1):
    """Returns the number of players currently registered."""
    (database, cursor) = connect()
    cursor.execute("SELECT count(*) FROM players WHERE tournament_id = %s;", (tournament_id,))
    number_of_players = cursor.fetchone()
    database.close()
    return int(number_of_players[0])

def registerTournament(tournament_name):
    """Adds a tournament to the tournament database
    The database assigns a unique serial id number for the tournament.

    Args:
      tournament_name: the tournament's name (need not be unique).
    """
    clean_tournament_name = bleach.clean(tournament_name)
    (database, cursor) = connect()
    cursor.execute("INSERT INTO tournaments VALUES (DEFAULT, %s)", (clean_tournament_name, ))
    database.commit()
    database.close()

def registerPlayer(player_name, tournament_id = 1):
    """Adds a player to the player database.

    The database assigns a unique serial id number for the player.

    Args:
      player_name: the player's full name (need not be unique).
      tournament_id: the tournament's id.  If not provided, player will be              entered into tournament 1
    """
    # Quick check to see if tournament 1 exists
    if tournament_id == 1:
        (database, cursor) = connect()
        cursor.execute("SELECT tournament_id FROM tournaments WHERE tournament_id = 1")
        if cursor.fetchone() is None:
            database.close()
            registerTournament("Test Tournament")
        else:
            database.close()

    clean_player_name = bleach.clean(player_name)
    (database, cursor) = connect()
    cursor.execute("INSERT INTO players VALUES (%s, DEFAULT, %s)", (tournament_id, clean_player_name, ))
    database.commit()
    database.close()

def playerStandings(tournament_id = 1):
    """Player standing is calculated by a score assigned to each player.  Players are sorted from highest scoring to lowest scoring.
    Here is the scoring system:
        Win/Bye: +3
        Tie: +1
        OMW (Opponent Match Wins): + A fraction from 0-1, rounded to 2 decimal places. The fraction represents total wins / total matches for all the opponents of the player in question.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won.  Byes are not included here
        matches: the number of matches the player has played. Byes are not included here
    """
    (database, cursor) = connect()
    # Get the total record, filtered by the tournament in question
    cursor.execute("SELECT player_id, player_name, total_wins, total_matches, total_ties, bye FROM totalRecordWithMetadata WHERE tournament_id = %s", (tournament_id,))
    total_record = cursor.fetchall()
    database.close()
    player_standings = []
    # Loop through each player record tuple in total record, append the score to the tuple, and append the tuple to player_standings
    for player_record in total_record:
        player_id = player_record[0]
        OMW = calculate_OMW(player_id, total_record)
        wins = player_record[2]
        bye = player_record[5]
        ties = player_record[4]
        player_record += (((wins + bye)*3 + ties + OMW),)
        player_standings.append(player_record)
    # Now that the total record has a score value, sort the list by the score
    player_standings = sorted(player_standings, key = itemgetter(6), reverse = True)
    # Strip the total ties, bye, and score from each tuple
    player_standings = [player[0:4] for player in player_standings]
    return player_standings

def calculate_OMW(player_id, total_record):
    total_wins = 0
    total_matches = 0
    (database, cursor) = connect()
    # Get a list of all the opponents a player has had
    cursor.execute("SELECT opponent_one FROM matchRegistry WHERE opponent_two = %s UNION SELECT opponent_two FROM matchRegistry WHERE opponent_one = %s", (player_id,player_id,))
    opponents = cursor.fetchall()
    database.close()
    # If an opponent isn't even in the matchRegistry yet, just return 0
    if opponents == []:
        return 0
    # If a player hasn't had any opponents, just return 0
    if opponents[0][0] is None:
        return 0
    # Loop through the list of opponents
    for opponent in opponents:
        # Find which index position in the total record has the opponent's record
        opponent_index_in_record = [i for i, v in enumerate(total_record) if v[0] is opponent[0]]
        # Grab that opponent's wins and matches, and add them to the total wins and total matches respectively
        total_wins += total_record[opponent_index_in_record[0]][2]
        total_matches += total_record[opponent_index_in_record[0]][3]
    return round((float(total_wins)/total_matches), 2)

def reportMatch(winner, loser, tie = None, bye = None, tournament_id = None):
    """Records the outcome of a single match between two players. User must pass
    in values for winner and loser. tie is optional.

    Args:
        winner: the id number of the player who won.  If this match is a bye, insert the id of the player who received the bye here.  Leave the loser blank.
        loser: the id number of the player who lost.
        tie: pass in True if the players tied.  In this case, the parameters for winner and loser don't represent a winner or loser.  They represent participants who tied.
        bye: pass in True if the player in the winner parameter recieved a bye.
        tournament: pass in the id of the tournament which the match is part of.  If tournament isn't passed in, the player id's will be looked up.
    """
    # Look up which tournament the players are a part of, using the winner.  This assumes the winner and loser are in the same tournament, which they should be
    if not tournament_id:
        (database, cursor) = connect()
        cursor.execute("SELECT tournament_id FROM players WHERE player_id = %s", (winner,))
        tournament_id = cursor.fetchone()[0]
        database.close()
        if not tournament_id:
            raise ValueError("player must be a part of a tournament")
    # Check for byes first, since this is the only scoring element that only involves the winner parameter, and not the loser parameter
    if winner and bye and not (loser or tie):
        (database, cursor) = connect()
        # First register the match
        cursor.execute("INSERT INTO matchRegistry (tournament_id, match_id, opponent_one) VALUES (%s, DEFAULT, %s)", (tournament_id, winner))
        database.commit()
        # Pull the match ID that was just committed
        cursor.execute("SELECT match_id from matchRegistry WHERE opponent_one = %s", (winner,))
        match_id = cursor.fetchone()[0]
        # Insert the bye into the records table
        cursor.execute("INSERT INTO records (tournament_id, match_id, player_id, bye) VALUES (%s, %s, %s, True)", (tournament_id, match_id, winner,))
        # Stop execution because all interaction with database for bye is finished and we don't want to continue executing and setting more unneccary info to database
        database.commit()
        database.close()
        return None
    # A couple of sanity checks
    if not (type(winner) is int and type(loser) is int):
        raise ValueError("user must pass in integers")
    if tie and (not type(tie) is bool):
        raise ValueError("user must pass in tie as a boolean")
    if winner and loser and bye:
        raise ValueError("if user is trying to submit a bye, only winner parameter can be passed in")

    (database, cursor) = connect()
    # Register the match.  always store the smaller player_id in the opponent_one spot to avoid repeat matches IN the sql index
    if winner > loser:
        cursor.execute("INSERT INTO matchRegistry VALUES (%s, DEFAULT, %s, %s)",
                  (tournament_id, loser, winner,))
        database.commit()
        cursor.execute("SELECT match_id from matchRegistry WHERE (opponent_one = %s AND opponent_two = %s)", (loser, winner,))
        match_id = cursor.fetchone()[0]
    if loser > winner:
        cursor.execute("INSERT INTO matchRegistry VALUES (%s, DEFAULT, %s, %s)",
                  (tournament_id, winner, loser,))
        database.commit()
        cursor.execute("SELECT match_id from matchRegistry WHERE (opponent_one = %s AND opponent_two = %s)", (winner, loser,))
        match_id = cursor.fetchone()[0]
    # Now log the ties (if applicable)
    if tie == True:
        cursor.execute("INSERT INTO records (tournament_id, match_id, player_id, tie) VALUES (%s, %s, %s, True)", (tournament_id, match_id, winner))
        cursor.execute("INSERT INTO records (tournament_id, match_id, player_id, tie) VALUES (%s, %s, %s, True)", (tournament_id, match_id, loser))
    # Log the regular wins/losses if not ties
    else:
        cursor.execute("INSERT INTO records (tournament_id, match_id, player_id, win) VALUES (%s, %s, %s, True)", (tournament_id, match_id, winner,))
        cursor.execute("INSERT INTO records (tournament_id, match_id, player_id, loss) VALUES (%s, %s, %s, True)", (tournament_id, match_id, loser,))
    database.commit()
    database.close()

def swissPairings(tournament_id = 1):
    """Returns a list of pairs of players for the next round of a match.

    Each player is paired with another player with an equal or nearly-equal win record, that is, a player adjacent to him or her in the standings.

    If there are an odd number of players, the last player returned will be the one which receives a bye.  This player will be the one with the lowest standing, and will not have been assigned a bye before (only one bye per player)

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
      In the case of an odd number of players, the last tuple will have this form
        id: the player's id receiving a bye
        name: the player's name receiving a bye
    """
    player_standings = playerStandings(tournament_id)
    number_of_players = len(player_standings)
    # First handle the situation where there are an odd number of players
    if number_of_players % 2 == 1:
        (database, cursor) = connect()
        # To give the lowest ranking players byes, first reverse the player standings
        reverse_player_standings = sorted(player_standings, reverse = True)
        for (place, player_record) in enumerate(reverse_player_standings):
            player_id = player_record[0]
            # Check if this player's received a bye before
            cursor.execute("SELECT count(bye) FROM records WHERE (tournament_id = %s AND player_id = %s) GROUP BY player_id;", (tournament_id, player_id,))
            bye = cursor.fetchone()
            # If this player hasn't had a bye before, short circuit the loop, create the swisspairings tuples and return them
            if bye == 0:
                database.close()
                # Calculate the index position of this player in the player_standings list of tuples
                index_position = number_of_players - place
                # Remove the tuple of the player getting the bye from the player_standings list
                even_player_standings = player_standings[0 : index_position] + player_standings[index_position + 1:]
                # Grab the tuple getting the bye from the player_standings list
                bye = player_standings[index_position : index_position + 1]
                swissPairings = swissPairingsHelper(even_player_standings, bye)
                return swissPairings
    # If there are an even number of players, it's just a matter of calling swissPairingsHelper
    else:
        swissPairings = swissPairingsHelper(player_standings)
        return swissPairings

def swissPairingsHelper(even_player_standings, bye = False):
    """Does the actual work of swissPairings. Look at the docstring of that function to see the expected return of this function.

      Args:
        even_player_standings: A list of tuples from player_standings.  Must have an even number of players
        bye: pass in a single player tuple from a player_standings list.  This player will receive a bye and will be placed at the end of the resulting swissPairings list
    """
    swissPairings = []
    # This for loop creates the swissPairings for an even amount of players
    for (place, player_record) in enumerate(even_player_standings):
        player_id = player_record[0]
        player_name = player_record[1]
        if place % 2 == 0:
            first_player = (player_id, player_name)
        if place % 2 == 1:
            swissPairings.append(first_player + (player_id, player_name,))
    # If a player receives a bye, that player's tuple is inserted at the end of the swissPairings here
    if bye:
        player_id = bye[0]
        player_name = bye[1]
        swissPairings.append((player_id, player_name))
    return swissPairings
