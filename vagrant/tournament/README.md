# Tournament Database
This is a tournament database engine created as project 2 of [Udacity's Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).  

## Features
* Keeps track of players and matches in a tournament
* Supports ties
* Uses the Swiss pairing system for pairing players together  
* Supports more than one tournament in the database
* Prevents rematches between players
* A tournament can host either an even or odd number of players
  * In the case of an odd number of players, the weakest player receives a bye each round
  * A player cannot receive more than one bye in a tournament

## Scoring System
* Each player receives a score, which determines the swiss pairings for the next round of the tournament
* Here is how the score is calculated:
  * +3: Win
  * +1: Tie
  * +0 ≤ OMW ≤ 1
    * OMW stands for Opponent Matched Wins
    * It is a decimal between 0 and 1 rounded to 2 decimal places
    * It is calculated as total number of wins by players played against divided by the total number of matches by players played against

## Setup
* Secure shell into the [vagrant VM](https://www.vagrantup.com/docs/getting-started/) installed in this github repository
* Enter the [psql command line](http://www.postgresql.org/docs/8.4/static/tutorial-accessdb.html) by typing `psql` in the tournament directory
* Use the command `\i tournament.sql` to import the database schema into psql
* The database can now be manipulated  in two ways:
  * In psql using sql commands directly
  * In the python interpreter by using the command `import tournament`, and using the methods in tournament.py

## Testing
To test the database engine, run `python tournament_test.py` at the command line in the tournament directory.  Make sure to Run the setup steps before running `tournament_test.py`

## Dependencies
* Python v 2.7
