import io
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai
import pandas as pd
import streamlit as st
from stqdm import stqdm
from streamlit.runtime.scriptrunner import add_script_run_ctx

from csv_translator.components.sidebar import sidebar
from csv_translator.core.translation import translate_to_language_openai
from csv_translator.ui import (
    is_open_ai_key_valid,
)

st.set_page_config(page_title="TranslateCSV", page_icon="📖", layout="wide")
st.header("TranslateCSV")

sidebar()

openai_api_key = st.session_state.get("OPENAI_API_KEY")


def save_translated_data_to_buffer(data, columns_to_translate, lang):
    unique_values = set()
    for col in columns_to_translate:
        unique_values.update(data[col].unique())

    pbar = stqdm(total=len(unique_values), desc=f"Translating {lang}")

    # Callback function to update the tqdm progress bar
    def update_progress(future):
        pbar.update(1)

    with ThreadPoolExecutor(max_workers=16) as executor:
        # Use submit instead of map to get futures.
        futures = [executor.submit(translate_to_language_openai, value, lang) for
                   value in unique_values]

        for t in executor._threads:
            add_script_run_ctx(t)

        # Attach the update callback to each future.
        for future in futures:
            future.add_done_callback(update_progress)

        # Collect the results.
        results = [future.result() for future in as_completed(futures)]
    translations = {}

    for value, translation in results:
        translations[value] = translation

    for col in columns_to_translate:
        data[col] = data[col].map(translations)

    buffer = io.BytesIO()
    translated_data.to_csv(buffer, encoding='utf-8-sig', index=False)
    buffer.seek(0)
    return buffer


if not openai_api_key:
    st.warning(
        "Enter your OpenAI API key in the sidebar. You can get a key at"
        " https://platform.openai.com/account/api-keys."
    )

uploaded_file = st.file_uploader(
    "Upload a csv file",
    type=["csv"],
)

if not uploaded_file:
    st.stop()

st.session_state.uploaded_file = uploaded_file

data_pd = pd.read_csv(uploaded_file)
st.write("Uploaded CSV Data")
st.write(data_pd)

# Let the user select a column
column_to_translate = st.multiselect("Select columns to translate", data_pd.columns)

languages = [
    "Spanish", "German", "French", "Italian", "Dutch", "Arabic", "Japanese", "Korean"
]

selected_languages = st.multiselect("Select languages", languages)

if "translated_buffers" not in st.session_state:
    st.session_state.translated_buffers = {}

btn = st.button("Translate")

if btn:
    if not is_open_ai_key_valid(openai_api_key):
        st.stop()

    openai.api_key = openai_api_key
    with st.spinner("Translating documents.. This may take a while, do not reload page⏳"):
        for lang in selected_languages:
            translated_data = data_pd.copy()
            buffer = save_translated_data_to_buffer(
                translated_data, column_to_translate, lang
            )
            st.session_state.translated_buffers[lang] = buffer

for lang in selected_languages:
    if lang in st.session_state.translated_buffers:
        st.download_button(
            label=f"Download {lang} CSV",
            data=st.session_state.translated_buffers[lang],
            file_name=f"translated_{lang}.csv",
            mime="text/csv"
        )
