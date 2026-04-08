import httpx
import json
import streamlit as st


st.title("🗨️ Chat Assistant")

thread_id = st.sidebar.text_input(label="Conversation",value="Thread1")

if 'messages' not in st.session_state:
    st.session_state.messages = []

query = st.chat_input("Hello, How can I help you today?")
if query:
    st.session_state.messages.append({'role':'user','content':query})

    with st.chat_message('user'):
        st.markdown(query)
    
    with st.chat_message('assistant'):
        tool_container = st.container()

        placeholder = st.empty()
        full_response = ""

        with httpx.Client(timeout=None) as client:
            with client.stream("POST","http://127.0.0.1:8000/chat_stream",
                                json={"query": query, "thread_id":thread_id}) as response:
                print("Coming back here...")
                for line in response.iter_lines():
                    print(line)
                    if not line.strip():
                        continue

                    chunk = json.loads(line)
                    print(chunk)
                    msg_type = chunk.get("type","")
                    content = chunk.get("content","")

                    if content and "AIMessage" in msg_type:
                        full_response = full_response + content
                        placeholder.markdown(full_response.replace("$", "\\$"))
    st.session_state.messages.append({'role':'assistant','content':full_response})
