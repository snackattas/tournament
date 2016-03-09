# Tournament Database
This is a tournament database engine created as project 2 of [Udacity's Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).  

## Features
* Keeps track of players and matches in a tournament
* Supports ties
* Uses the Swiss Pairing system for pairing players together  
* Supports more than one tournament in the database
* Prevents rematches between players
* A tournament can host either an even or odd number of players
  * In the case of an odd number of players, the weakest player receives a bye each round
  * A player cannot receive more than one bye in a tournament

## Scoring System
* Each player receives a score, which determines the Swiss Pairings for the next round of the tournament
* Here is how the score is calculated:
  * +3: Win
  * +1: Tie
  * +0 ≤ OMW ≤ 1
    * OMW stands for Opponent Matched Wins
    * It is a decimal between 0 and 1 rounded to 2 decimal places
    * It is calculated as total number of wins by players played against divided by the total number of matches by players played against

## Functions in tournament.py
#### registerTournament(tournament_name)
Adds a tournament to the tournament database. The database assigns a unique id number to the tournament.
#### registerPlayer(player_name, tournament_id)
Adds a player to a specific tournament. The database assigns a unique ID number to the player. Different players may have the same names but will receive different ID numbers.
#### countPlayers(tournament_id)
Returns the number of players currently registered in a specific tournament.
#### deleteTournament(tournament_id)
Removes the specified tournament.  All the tournament's players, matches, and records are also removed.
#### deleteMatches(tournament_id)
Removes all the match records from the database for a specific tournament.
#### deletePlayers(tournament_id)
Clear out all the player records from the database for a specific tournament.
#### reportMatch(winner, loser, tie=None, bye=None, tournament_id)
Records the outcome of a single match between two players in the same tournament.  Also able to record byes for a single player.
#### playerStandings(tournament_id)
Returns a list of (id, name, wins, matches) for each player in the tournament.  Player standing is calculated by a score assigned to each player.  Players are sorted from highest to lowest scoring.
#### swissPairings(tournament_id)
Returns a list of pairs of players for the next round of a match.  Each player is paired with the adjacent player in the standings.  If there are an odd number of players, the last player returned (the one with the lowest standing) will be the one which receives a bye.

## Setup
* Secure shell into the [vagrant VM](https://www.vagrantup.com/docs/getting-started/) installed in this github repository
* Enter the [psql command line](http://www.postgresql.org/docs/8.4/static/tutorial-accessdb.html) by typing `psql` in the tournament directory
* Use the command `\i tournament.sql` to import the database schema into psql
* The database can now be manipulated  in two ways:
  * In psql using sql commands directly
  * In the python interpreter by using the command `import tournament`, and using the methods in tournament.py

## Testing
To test the database, run `python tournament_test.py` at the command line in the tournament directory.  Make sure to run the setup steps before using `tournament_test.py`

## Dependencies
Python v 2.7
