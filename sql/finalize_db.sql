CREATE INDEX idx_search ON journal.entries USING GIN(search);

------------------------------------------------------------

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
    
------------------------------------------------------------

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

------------------------------------------------------------

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