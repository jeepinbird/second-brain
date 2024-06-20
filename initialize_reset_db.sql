-- Set up pgvector extension if not already there.
-- Must be executed by superuser. Only has to be run once.
/*
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
*/

DROP TEXT SEARCH CONFIGURATION IF EXISTS simple_unaccent;
CREATE TEXT SEARCH CONFIGURATION simple_unaccent ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION simple_unaccent ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple;

DROP TEXT SEARCH CONFIGURATION IF EXISTS english_unaccent;
CREATE TEXT SEARCH CONFIGURATION english_unaccent ( COPY = english );
ALTER TEXT SEARCH CONFIGURATION english_unaccent ALTER MAPPING FOR hword, hword_part, word WITH unaccent, english_stem;

DROP TABLE IF EXISTS journal.events CASCADE;
DROP TABLE IF EXISTS journal.entries CASCADE;

CREATE TABLE journal.entries (
    id BIGSERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    weight NUMERIC,
    wx_cond TEXT,
    wx_high NUMERIC,
    wx_low NUMERIC,
    blurb TEXT,
    tags TEXT,
    search TSVECTOR
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english_unaccent', COALESCE(blurb,'')), 'A') || ' ' || 
            setweight(to_tsvector('simple_unaccent', COALESCE(REPLACE(tags, '/', ' '),'')), 'B') :: tsvector 
        ) STORED
);

CREATE TABLE journal.events (
    id BIGSERIAL PRIMARY KEY,
    entry_id BIGINT NOT NULL REFERENCES journal.entries(id),
    content TEXT NOT NULL,
    search TSVECTOR GENERATED ALWAYS AS (to_tsvector('english_unaccent', content)::tsvector) STORED
);
