import ollama
import search
import streamlit as st

st.title("Second Brain")

# initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# init models
def get_available_models():
    models = [model["name"] for model in ollama.list()["models"]]
    models.remove('nomic-embed-text:latest')
    models.sort()
    return models

if "model" not in st.session_state:
    st.session_state["model"] = ""

# build out the sidebar
with st.sidebar:
    # Allow choice of available models
    st.session_state["model"] = st.selectbox("Choose your model", get_available_models())

    # Button to reset session state
    if st.button("Clear session"):
        st.session_state["messages"] = []
        if "initial_prompt" in st.session_state:
            del st.session_state["initial_prompt"]

# Get initial context from the database
@st.cache_data(show_spinner='Fetching context from PostgreSQL')
def get_context(prompt):
    return search.get_context(prompt)

# Generate streaming response
def model_resp_generator():
    stream = ollama.chat(
        model=st.session_state["model"],
        messages=st.session_state["initial_context"] + st.session_state["messages"],
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter prompt here"):
    # add latest message to history in format {role, content}
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # initialize database connection and check database for answers
    if "initial_prompt" not in st.session_state:
        st.session_state["initial_prompt"] = prompt
        st.session_state["initial_context"] = [{"role": "user", "content": f"Using the following text from my personal journal as a resource\n```\n{get_context(prompt)}\n```\n\nAnswer the question: {prompt}"}]
        print(f"\n\nprompt: {st.session_state["initial_prompt"]}")
        print(f"\ncontext: {st.session_state["initial_context"]}")

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_resp_generator())
        st.session_state["messages"].append({"role": "assistant", "content": message})

