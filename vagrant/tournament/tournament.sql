-- Each time you want to reload this database, enter the psql environment and run this command:
-- "\i tournament.sql"
--The four commands below will delete the old tournament database and recreate a new tournament database
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE tournaments (
    tournament_id serial PRIMARY KEY
,   tournament_name varchar(254)
);

CREATE TABLE players (
    tournament_id integer REFERENCES tournaments(tournament_id)
,   player_id serial PRIMARY KEY
,   player_name varchar(254)
,   player_standing decimal
);

-- This is the match registry table.  Every row gets a match serial number.
-- In the case of a normal match, opponent_one and opponent_two will be populated.
-- In the case of a bye, only opponent_one will be populated, opponent_two will be null.
CREATE TABLE matchRegistry (
    tournament_id integer REFERENCES tournaments(tournament_id)
,   match_id serial PRIMARY KEY
,   opponent_one integer REFERENCES players(player_id)
,   opponent_two integer REFERENCES players(player_id)
    CHECK (opponent_one != opponent_two)
);
-- This index prevents rematches between the same players.  The python code that registers matches always sets the smaller player_id in the opponent_one slot, enforcing this reverseMatchRegistry
CREATE UNIQUE INDEX reverseMatchRegistry
ON matchRegistry(opponent_one, opponent_two);

--The paradigm in this table is that the columns win/loss/tie/bye will only ever be populated with true.  There's no need to populate them with false.
CREATE TABLE records (
    tournament_id integer REFERENCES tournaments(tournament_id)
,   match_id integer REFERENCES matchRegistry(match_id)
,   player_id integer REFERENCES players(player_id)
,   win boolean
,   loss boolean
,   tie boolean
,   bye boolean
);

-- This index prevents the same player from receiving multiple byes
CREATE UNIQUE INDEX noPlayerWithTwoByes
ON records(player_id, bye);

-- The counts view creates important fields for calculating player standings
CREATE VIEW counts AS
SELECT
    player_id
,   count(win) AS total_wins
,   (count(win) + count(loss) + count(tie)) AS total_matches
,   count(tie) AS total_ties
,   count(bye) AS bye
FROM records
GROUP BY player_id;

-- The playerStandings view pulls identifying information from the players table and combines it with the count table.  It also does a coalesce operation and a left join to make sure that if a player doesn't have any matches yet, the player qill still show up here, albeit with a record full of 0's.
CREATE VIEW playerStandings AS
SELECT
    players.player_id
,   players.player_name
,   coalesce(counts.total_wins, 0) AS total_wins
,   coalesce(counts.total_matches, 0) AS total_matches
,   coalesce(counts.total_ties, 0) AS total_ties
,   coalesce(counts.bye, 0) AS bye
,   players.tournament_id
,   coalesce(players.player_standing, 0) AS player_standing
FROM players LEFT JOIN counts
ON players.player_id = counts.player_id
ORDER BY player_standing DESC;
