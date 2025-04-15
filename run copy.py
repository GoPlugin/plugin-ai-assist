import streamlit as st
import requests


# Streamlit app configuration
# st.logo("logo-plugin-color.png",size="medium", link=None, icon_image=None)
st.set_page_config(page_title="Plugin AI Assist",page_icon="🚀")

# Add custom CSS to adjust logo size
# Add custom CSS to adjust logo size
st.markdown("""
<style>
img[alt="Logo"] {
    height: 100px; /* Set your desired height */
    width: auto; /* Maintain aspect ratio */
}
</style>
""", unsafe_allow_html=True)

# Display the logo
st.logo("logo-plugin-color.png")  # Replace with your logo file path
st.title("Plugin(Decentralized Oracle) - AI Assist")
st.write("Ask Anything about Plugin & it's Eco System")

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000/query"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"],avatar="🧑‍💻" if message["role"] == "user" else "🚀"  ):
        st.markdown(message["content"])

# Input box for user query
if user_input := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user","content": user_input})
    with st.chat_message("user",avatar="🧑‍💻"):
        st.markdown(user_input)

    # Send query to FastAPI backend
    try:
        response = requests.post(BACKEND_URL,json={"query": user_input})
        response.raise_for_status()
        bot_response = response.json().get("response","No response received")
    except requests.RequestException as e:
        bot_response = f"Error: Could not connect to backend ({str(e)})"

    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant","content": bot_response})
    with st.chat_message("assistant",avatar="🚀"):
        st.markdown(bot_response)