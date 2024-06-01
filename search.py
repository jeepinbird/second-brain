import os
import sys
import toml
import ollama
import psycopg
import numpy as np
import pandas as pd
from pgvector.psycopg import register_vector

# Read the password from the TOML file
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
                # Execute queries and fetch results into pandas DataFrames
                results1 = pd.read_sql("SELECT date, blurb, content FROM journal.search_events(%s)", conn, params=(query_string,))
                results2 = pd.read_sql("SELECT date, blurb, '' AS content FROM journal.search_entries(%s) LIMIT 20", conn, params=(query_string,))
                results3 = pd.read_sql("SELECT a.date, a.blurb, b.content FROM journal.entries a JOIN journal.events b ON b.entry_id = a.id ORDER BY b.embedding <-> %s LIMIT 10", conn, params=(embed_qry,))
                
                # Combine all results into a single DataFrame
                results = pd.concat([results1, results2, results3])
            except psycopg.Error as e:
                print("Error occurred: {}",format(e))
            else:
                return results
    except psycopg.OperationalError as e:
        print("Unable to connect to the database: {}".format(e))

query = sys.argv[1]

docs = get_context(query)

# Extract the relevant content from the DataFrame
context = "\n\n".join([f"{row['date']}: {row['blurb']} - {row['content']}" for _, row in docs.iterrows()])

modelquery = f"Using the following text from my personal journal as a resource\n```\n{context}\n```\n\nAnswer the question: {query}"

stream = ollama.generate(model='llama3', prompt=modelquery, stream=True)

for chunk in stream:
  if chunk["response"]:
    print(chunk['response'], end='', flush=True)

print()