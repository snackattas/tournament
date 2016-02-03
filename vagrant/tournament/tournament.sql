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

CREATE TABLE matches
(
    match serial PRIMARY KEY,
    winner integer REFERENCES players(player_id),
    loser integer REFERENCES players(player_id),
    tie boolean,
    CHECK (winner != loser)
);

CREATE VIEW wins_total AS
SELECT players.player_id AS player_id, count(matches.winner) AS wins
FROM players LEFT OUTER JOIN matches
ON players.player_id = matches.winner
WHERE matches.tie != true
GROUP BY players.player_id;

CREATE VIEW losses_total AS
SELECT players.player_id AS player_id, count(matches.loser) AS losses
FROM players LEFT OUTER JOIN matches
ON players.player_id = matches.loser
WHERE matches.tie != true
GROUP BY players.player_id;

CREATE VIEW ties_total AS
SELECT winner AS player_id, count(winner) AS ties
FROM matches WHERE tie = true
GROUP BY winner
UNION
SELECT loser AS player_id, count(loser) AS ties
FROM matches WHERE tie = true
GROUP BY loser;



CREATE VIEW record AS
SELECT wins_player_id FROM wins_total JOIN losses_total ON
wins_total.player_id = losses_total.player_id), wins_total.wins,
losses_total.losses;
