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
);

-- This is the match registry table.  Every row gets a match serial number.
-- In the case of a normal match, opponent_one and opponent_two will be populated.
-- In the case of a bye, only opponent_one will be populated, opponent_two will be null,
-- and bye will be true.
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

--The paradigm in this table is that the columns win/loss/tie/bye will only every be populated with true.  There's no need to populate them with false.
CREATE TABLE records (
    tournament_id integer REFERENCES tournaments(tournament_id)
,   match_id integer REFERENCES matchRegistry(match_id)
,   player_id integer REFERENCES players(player_id)
,   win boolean
,   loss boolean
,   tie boolean
,   bye boolean
);

CREATE UNIQUE INDEX noPlayerWithTwoByes
ON records(player_id, bye);

CREATE VIEW totalRecord AS
SELECT
    player_id
,   count(win) AS total_wins
,   (count(win) + count(loss) + count(tie)) AS total_matches
,   count(tie) AS total_ties
,   count(bye) AS bye
FROM records
GROUP BY player_id, tournament_id
ORDER BY player_id;

CREATE VIEW totalRecordWithName AS
SELECT
    players.tournament_id
,   players.player_id
,   players.player_name
,   coalesce(totalRecord.total_wins, 0) AS total_wins
,   coalesce(totalRecord.total_matches, 0) AS total_matches
,   coalesce(totalRecord.total_ties, 0) AS total_ties
,   coalesce(totalRecord.bye, 0) AS bye
FROM players LEFT JOIN totalRecord
ON players.player_id = totalRecord.player_id;
