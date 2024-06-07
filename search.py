import toml
import ollama
import psycopg
import numpy as np
from pgvector.psycopg import register_vector

# Read the password from the TOML secrets file
config = toml.load('.streamlit/secrets.toml')
db_config = config['connections']['second_brain']

def connect_db():
    return psycopg.connect(
        host=db_config['host'],
        dbname=db_config['database'],
        user=db_config['username'],
        password=db_config['password'],
        autocommit=False
    )

def get_context(query_string):
    # Generate embedded query
    embed_qry = np.array(ollama.embeddings(model='nomic-embed-text', prompt=query_string)['embedding'])
        
    try:
        with connect_db() as conn:
            # Set up pgvector on the connection
            register_vector(conn)
            
            # Attempt to find relevant context using these various queries
            try:
                results = conn.execute("SELECT date, CASE WHEN blurb IS NULL THEN '' ELSE blurb || ' - ' END AS blurb, '' AS content FROM journal.search_entries(%s)", (query_string,)).fetchall()
                results.extend(conn.execute("SELECT date, CASE WHEN blurb IS NULL THEN '' ELSE blurb || ' - ' END AS blurb, content FROM journal.search_events(%s) LIMIT 20", (query_string,)).fetchall())
                results.extend(conn.execute("SELECT a.date, CASE WHEN a.blurb IS NULL THEN '' ELSE a.blurb || ' - ' END AS blurb, b.content FROM journal.entries a JOIN journal.events b ON b.entry_id = a.id ORDER BY b.embedding <-> %s LIMIT 20", (embed_qry,)).fetchall())
            except psycopg.Error as e:
                print("Error occurred: {}",format(e))
    except psycopg.OperationalError as e:
        print("Unable to connect to the database: {}".format(e))
    
    context = "\n\n".join([f"{date}: {blurb}{content}" for date, blurb, content in results])
    return context

if __name__ == "__main__":
    import sys
    
    # Get the prompt from CLI
    query = sys.argv[1]

    # Fetch the related context from the database
    context = get_context(query)
    print(context)

    # Build a prompt
    modelquery = f"Using the following text from my personal journal as a resource\n```\n{context}\n```\n\nAnswer the question: {query}"

    # Generate a response from the model
    response = ollama.generate(model='llama3', prompt=modelquery, stream=True)

    # # Loop through the streaming response and print out the results
    for chunk in response:
        if chunk["response"]:
            print(chunk['response'], end='', flush=True)
    print()
