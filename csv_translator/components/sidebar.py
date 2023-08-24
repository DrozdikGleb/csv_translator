import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload a csv file📄\n"
            "3. Choose columns and languages💬\n"
            "4. Press 'Translate' button and wait a little bit⌛\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",
            # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
                  or st.session_state.get("OPENAI_API_KEY", ""),
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input
