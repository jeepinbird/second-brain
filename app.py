import ollama
import streamlit as st

st.title("Second Brain")

# initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# init models
@st.cache_data
def get_available_models():
    models = [model["name"] for model in ollama.list()["models"]]
    models.remove('nomic-embed-text:latest')
    models.sort()
    return models

if "model" not in st.session_state:
    st.session_state["model"] = ""


# Reset session state
with st.sidebar:
    st.session_state["model"] = st.selectbox("Choose your model", get_available_models())

    if st.button("Clear session"):
        st.session_state["messages"] = []
        if "initial_prompt" in st.session_state:
            del st.session_state["initial_prompt"]

# Generate streaming response
def model_res_generator():
    stream = ollama.chat(
        model=st.session_state["model"],
        messages=st.session_state["messages"],
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
        st.write(f"initial_prompt: {prompt}")
        st.session_state["initial_prompt"] = prompt
        #conn = st.connection('second_brain', type='sql')

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator())
        st.session_state["messages"].append({"role": "assistant", "content": message})

