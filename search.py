import toml
import ollama
import psycopg
import numpy as np
from pgvector.psycopg import register_vector

# Read the password from the TOML secrets file
config = toml.load('.streamlit/secrets.toml')
db_config = config['connections']['second_brain']

def connect_db():
    connection = psycopg.connect(
                host=db_config['host'],
                dbname=db_config['database'],
                user=db_config['username'],
                password=db_config['password'],
                autocommit=False
            )
    
    # Set up pgvector on the connection
    register_vector(connection)

    return connection

def get_context(query_string):
    try:
        with connect_db() as conn:
            # Attempt to find relevant context using these various queries
            try:
                results = conn.execute("SELECT date, CASE WHEN blurb IS NULL THEN '' ELSE blurb || ' - ' END AS blurb, '' AS content FROM journal.search_entries(%s)", (query_string,)).fetchall()
                results.extend(conn.execute("SELECT date, CASE WHEN blurb IS NULL THEN '' ELSE blurb || ' - ' END AS blurb, content FROM journal.search_events(%s) LIMIT 20", (query_string,)).fetchall())
            except psycopg.Error as e:
                print("Error occurred: {}",format(e))
    except psycopg.OperationalError as e:
        print("Unable to connect to the database: {}".format(e))
    
    context = "\n\n".join([f"{date}: {blurb} - {content}" for date, blurb, content in results])
    return context

if __name__ == "__main__":
    import sys
    
    try:
        query = sys.argv[1]
    except IndexError:
        print(f'\n  Usage: search.py "Why is the sky blue?"\n')
        quit()

    streamed_response = True
    try:
        if run_type := sys.argv[2]:
            if run_type == 'no_stream':
                streamed_response = False
    except IndexError:
        pass

    context = get_context(query)

    modelquery = f"Using the following text from my personal journal as a resource\n```\n{context}\n```\n\nAnswer the question: {query}"

    response = ollama.generate(model='llama3', prompt=modelquery, stream=streamed_response)

    if streamed_response:
        for chunk in response:
            if chunk["response"]:
                print(chunk['response'], end='', flush=True)
    else:
        print(f"Evaluated {response['prompt_eval_count']} tokens and generated the full response in {response['total_duration'] / 1000000000} seconds.")
        print(response["response"])

    # End with a new line
    print()