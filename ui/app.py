import streamlit as st

st.set_page_config(
    page_title="BoardBot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 BoardBot")
st.caption("AI Workspace Booking & Scheduling Agent")

st.divider()

st.subheader("💬 Chat with BoardBot")

user_message = st.chat_input("Ask BoardBot to book or manage a room...")

if user_message:
    st.chat_message("user").write(user_message)
    st.chat_message("assistant").write(
        "BoardBot is ready. API integration is coming next."
    )