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
CREATE DATABASE tournament;
\c tournament;
