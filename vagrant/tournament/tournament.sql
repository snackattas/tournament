--Run this command on the psql command line to create the tournament DATABASE
--\i tournament.sql
-- CREATE FUNCTION does_tournament_exist () RETURNS text AS $$
-- DECLARE
-- name TEXT;
-- BEGIN
-- name := SELECT datname FROM pg_catalog.pg_database WHERE datname='tournament';
-- RETURN name;
-- END $$;
-- IF does_tournament_exist()='tournament' THEN DROP DATABASE tournament;
-- END IF;
-- Create database "tournament" and connect to that database before creating tables
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players
(
    player_id serial PRIMARY KEY,
    player_name text
);

CREATE TABLE match_registry
(
    match serial PRIMARY KEY,
    opponent_one integer REFERENCES players(player_id),
    opponent_two integer REFERENCES players(player_id),
    CHECK (opponent_one != opponent_two)
);
-- This index prevents rematches between players
CREATE UNIQUE INDEX reverse_match_reg ON match_registry(opponent_one, opponent_two);

CREATE TABLE records
(
    match integer REFERENCES match_registry(match),
    player_id integer REFERENCES players(player_id),
    win boolean,
    loss boolean,
    tie boolean
);

-- This view shows only wins.
-- Players who haven't played yet or who don't have wins won't show up.
CREATE VIEW only_wins AS
SELECT player_id,
count(win) AS wins
FROM records
WHERE win = true
GROUP BY player_id;

-- This view shows wins.
-- Players who haven't played yet or who don't have wins show up as 0.
CREATE VIEW wins AS
SELECT players.player_id,
coalesce(only_wins.wins, 0) AS wins
FROM players LEFT JOIN only_wins
ON players.player_id = only_wins.player_id;

-- This view shows only losses.
-- Players who haven't played yet or who don't have losses won't show up.
CREATE VIEW only_losses AS
SELECT player_id,
count(loss) AS losses
FROM records
WHERE loss = true
GROUP BY player_id;

-- This view shows losses.
-- Players who haven't played yet or who don't have losses show up as 0.
CREATE VIEW losses AS
SELECT players.player_id,
coalesce(only_losses.losses, 0) AS losses
FROM players LEFT JOIN only_losses
ON players.player_id = only_losses.player_id;

-- This view shows only ties.
-- Players who haven't played yet or who don't have ties won't show up.
CREATE VIEW only_ties AS
SELECT player_id, count(tie) AS ties
FROM records
WHERE tie = true
GROUP BY player_id;

-- This view shows ties.
-- Players who haven't played yet or who don't have ties show up as 0.
CREATE VIEW ties AS
SELECT players.player_id,
coalesce(only_ties.ties, 0) AS ties
FROM players LEFT JOIN only_ties
ON players.player_id = only_ties.player_id;

-- These next couple of views manipulate the match_registry table to eventually
-- create the OMW (Opponent Match Wins), the total number of wins by player they
-- have played against.  Here's a sample of what the next couple of views are doing
-- Ex.
-- match | opponent_one | opponent_two
---------+--------------+--------------
--     1 |            1 |            2
--     2 |            1 |            3
-- TO:
-- match | opponent_two | opponent_one
---------+--------------+--------------
--     1 |            2 |            1
--     2 |            3 |            1
-- TO:
-- match | player_id    | opponent
---------+--------------+--------------
--     1 |            1 |            2
--     1 |            2 |            1
--     2 |            1 |            3
--     2 |            3 |            1
-- TO:
-- match | player_id    | opponent     | opponent_wins
---------+--------------+------------------------------
--     1 |            1 |            2 |            1
--     1 |            2 |            1 |            0
--     2 |            1 |            3 |            1
--     2 |            3 |            1 |            0
-- TO:
-- player_id    | OMW
---------+--------------+----
--            1 |         2 |
--            2 |         0 |
--            3 |         0 |
CREATE VIEW pre_OMW_1 AS
SELECT match, opponent_two, opponent_one
FROM match_registry;

CREATE VIEW pre_OMW_2 AS
SELECT * FROM match_registry
UNION
SELECT match,
opponent_two AS opponent_one,
opponent_one AS opponent_two
FROM pre_OMW_1
ORDER BY opponent_one ASC;

CREATE VIEW pre_OMW_3 AS
SELECT players.player_id AS player_id,
pre_OMW_2.opponent_two AS opponent
FROM players LEFT JOIN pre_OMW_2
ON players.player_id = pre_OMW_2.opponent_one;

CREATE VIEW pre_OMW_4 AS
SELECT pre_OMW_3.player_id AS player_id,
pre_OMW_3.opponent AS opponent,
coalesce(wins.wins,0) AS opponent_wins
FROM pre_OMW_3 LEFT JOIN wins
ON pre_OMW_3.opponent = wins.player_id;

CREATE VIEW OMW AS
SELECT player_id,
sum(opponent_wins) AS OMW
FROM pre_OMW_4
GROUP BY player_id;

-- These next couple of views join together previous wins, OMW, ties, andlosses
-- views to eventually create a "complete_record" view.
CREATE VIEW wins_and_ties AS
SELECT wins.player_id AS player_id,
wins.wins AS wins,
ties.ties AS ties
FROM wins JOIN ties
ON wins.player_id = ties.player_id
ORDER BY wins DESC,
ties DESC,
player_id ASC;

CREATE VIEW wins_ties_losses AS
SELECT wins_and_ties.player_id AS player_id,
wins_and_ties.wins AS wins,
wins_and_ties.ties AS ties,
losses.losses AS losses
FROM wins_and_ties JOIN losses
ON wins_and_ties.player_id = losses.player_id;

CREATE VIEW wins_ties_losses_OMW AS
SELECT  wins_ties_losses.player_id AS player_id,
wins_ties_losses.wins AS wins,
OMW.OMW AS OMW,
wins_ties_losses.ties AS ties,
wins_ties_losses.losses AS losses
FROM wins_ties_losses JOIN OMW
ON wins_ties_losses.player_id = OMW.player_id;

-- This is the complete_record view.  It has the wins, OMW, ties, losses, and
-- total matches played.  It is sorted as specified by the playerStandings function
CREATE VIEW complete_record AS
SELECT player_id,
wins,
OMW,
ties,
losses,
(wins + ties + losses) AS total_matches_played
FROM wins_ties_losses_OMW
ORDER BY wins DESC,
OMW DESC,
ties DESC,
losses ASC,
player_id ASC;

CREATE VIEW playerStandings AS
SELECT players.player_id,
players.player_name,
complete_record.wins,
complete_record.total_matches_played
FROM players JOIN complete_record
ON players.player_id = complete_record.player_id;

CREATE VIEW row_number AS
SELECT complete_record.player_id,
players.player_name,
row_number() OVER
(ORDER BY complete_record.wins DESC,
complete_record.OMW DESC,
complete_record.ties DESC,
complete_record.losses ASC,
complete_record.player_id ASC) AS row_number
FROM players join complete_record
ON players.player_id = complete_record.player_id;

CREATE VIEW player1 AS
SELECT player_id AS player_id_1,
player_name AS player_name_1,
row_number,
row_number() OVER
(ORDER BY row_number ASC) AS matching_row_number
FROM row_number
WHERE (row_number%2)=1;

CREATE VIEW player2 AS
SELECT player_id AS player_id_2,
player_name AS player_name_2,
row_number,
row_number() OVER
(ORDER BY row_number ASC) AS matching_row_number
FROM row_number
WHERE (row_number%2)=0;

CREATE VIEW swissPairings AS
SELECT player1.player_id_1,
player1.player_name_1,
player2.player_id_2,
player2.player_name_2
FROM player1, player2
WHERE player1.matching_row_number = player2.matching_row_number;
