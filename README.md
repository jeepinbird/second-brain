# Second Brain

This project is using local AI ([Ollama](https://ollama.ai/)) to read through my daily markdown journal entries, created via [Obsidian](https://obsidian.md/), to answer personal questions. The goal is to essentially enable the use of my journal as a source of long term memory, having the LLM (currently `llama3`) to analyze my questions and give me a "human" answer.

Example Questions:
- "When did we buy tires for the Passport?"
    - "How much did we pay for them?"
    - "Where did we buy them?"
    - "What brand were they?"
- "What is the name of my weight loss medicine?"
- "What were my son's first words?"

## Set up PostgreSQL Locally

### Install and configure the service

1. `sudo dnf install postgresql-server postgresql-contrib`
2. `sudo systemctl enable postgresql`
3. `sudo postgresql-setup --initdb --unit postgresql`
4. `sudo systemctl start postgresql`

### Set up database and user

1. `sudo -u postgres psql`
2. `CREATE USER youruser WITH PASSWORD 'yourpassword';`
3. `CREATE DATABASE second_brain OWNER youruser;`

### Create schema

*NOTE*: You must install and configure [pgvector](https://github.com/pgvector/pgvector) for this to work.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

DROP TEXT SEARCH CONFIGURATION IF EXISTS simple_unaccent CASCADE;
CREATE TEXT SEARCH CONFIGURATION simple_unaccent ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION simple_unaccent ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple;

DROP TEXT SEARCH CONFIGURATION IF EXISTS english_unaccent CASCADE;
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

CREATE INDEX idx_search ON journal.entries USING GIN(search);

DROP FUNCTION IF EXISTS journal.update_search_vector CASCADE;
CREATE FUNCTION journal.update_search_vector()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.search := to_tsvector('english', unaccent(NEW.content));
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_search_vector
    BEFORE INSERT OR UPDATE ON journal.events
    FOR EACH ROW
    EXECUTE FUNCTION journal.update_search_vector();

DROP FUNCTION IF EXISTS journal.search_entries;
CREATE FUNCTION journal.search_entries(qry TEXT)
    RETURNS TABLE (
    entry_id BIGINT,
    date DATE,
    blurb TEXT,
    tags TEXT
) AS
$$
SELECT id AS entry_id, date, blurb, tags
    FROM journal.entries
WHERE search @@ websearch_to_tsquery('english', qry)
    OR search @@ websearch_to_tsquery('simple', qry)
ORDER BY ts_rank(search, websearch_to_tsquery('english', qry))
        + ts_rank(search, websearch_to_tsquery('simple', qry)) DESC
LIMIT 50;
$$ LANGUAGE SQL;

DROP FUNCTION IF EXISTS journal.search_events;
CREATE FUNCTION journal.search_events(qry TEXT)
    RETURNS TABLE (
    event_id BIGINT,
    entry_id BIGINT,
    date DATE,
    blurb TEXT,
    tags TEXT,
    content TEXT
) AS
$$
SELECT a.id AS event_id, a.entry_id, b.date, b.blurb, b.tags, a.content
    FROM journal.events a
    JOIN journal.entries b ON b.id = a.entry_id
WHERE a.search @@ websearch_to_tsquery('english', qry)
    OR a.search @@ websearch_to_tsquery('simple', qry)
ORDER BY ts_rank(a.search, websearch_to_tsquery('english', qry))
        + ts_rank(a.search, websearch_to_tsquery('simple', qry)) DESC
LIMIT 50;
$$ LANGUAGE SQL;
```