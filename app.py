import streamlit as st
from pdf_to_csv import convert_to_csv
from query_handler import handle_query
from text_to_embedding import text_to_embedding
import sqlite3
import pandas as pd


def main():

    st.session_state.uploaded_file = True
    st.session_state.output = False
    st.session_state.process = False
    st.session_state.output_text = ""
    st.set_page_config(page_title="Query your pdfs")
    
    
    output1 = '''
    <div class="stTextInput" style="padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; background-color: #3b4252;">
    <div>{{MSG}}</div>
    </div>
    '''
    output2 = '''
    <div class="stTextInput" style="padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; background-color: #3b4252;">
    <div>{{MSG}}</div>
    </div>
    '''   
    _, cent_co, _ = st.columns(3)
    with cent_co:
        st.image("assets/logo.png", width=250)
    st.markdown(
        "<h1 style='text-align: center; color: white;'>Query: a Gemini App to Retrieve tabular data from pdfs</h1>",
        unsafe_allow_html=True,
    )
    user_question = st.text_input("Enter questions here:")
    if user_question:
        if st.session_state.uploaded_file:
            result = handle_query(user_question)
            st.write(output1.replace("{{MSG}}",result[0]),unsafe_allow_html=True)
            st.write(output2.replace("{{MSG}}",result[1]),unsafe_allow_html=True)
        else:
            st.error("Upload/Process Files before prompting")


    if st.session_state.uploaded_file:
        st.subheader("Parsed contents of the PDFs")
        try:
            conn = sqlite3.connect("./working/working.db")
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            st.session_state.tables = pd.read_sql(query, conn)

            for table_name in st.session_state.tables["name"]:
                st.write(f"Contents of {table_name} table")
                query = f"SELECT * FROM {table_name};"
                st.session_state.table_df = pd.read_sql(query, conn)
                st.dataframe(st.session_state.table_df)

            conn.close()
        except Exception as e:
            st.error(f"Error loading database: {e}")


if __name__ == "__main__":
    main()
