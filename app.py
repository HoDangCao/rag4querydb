import streamlit as st
from schema_extraction import *

from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain_community.vectorstores import FAISS 
from langchain.tools.retriever import create_retriever_tool

embeddings = SpacyEmbeddings(model_name='en_core_web_sm')

st.set_page_config(page_title="SQL Query Generator", page_icon=":mag:")

def main():
    st.title("Advanced Text to SQL")
    st.write("Generate SQL queries from natural language")

    ### Sidebar for uploading file
    st.sidebar.header("Configuration")
    default_db_url = "sqlite:///{}"
    
    # File uploader for database
    uploaded_files = st.sidebar.file_uploader("Upload a SQLite database", type=["db", "sqlite"], accept_multiple_files=True)
    st.sidebar.markdown("[Download sample database](https://drive.google.com/file/d/1RyTj-yCPlAwtQKfTThahZkMtDEKxi2Lr/view?usp=sharing)")
    
    if 'extracted_schemas' not in st.session_state:
        st.session_state.extracted_schemas = {}

    # Process the uploaded database
    if st.sidebar.button("Process Uploaded Database"):
        for file in uploaded_files:
            st.session_state.extracted_schemas[file.name] = extract_schema(default_db_url.format(file.name))
        st.sidebar.success('Done!')
    
    db_names = list(st.session_state.extracted_schemas.keys())
    col1, col2 = st.columns(2)
    if len(st.session_state.extracted_schemas) > 0:
        ### Show schemas at col1
        selected_db = col1.multiselect('Select database(s) to show schema(s)', db_names)
        selected_schemas = {db_name: st.session_state.extracted_schemas[db_name] for db_name in selected_db} 
        col1.write(selected_schemas)

        ### Remove SB at col1
        dbs_to_remove = col1.multiselect('Select database(s) to remove', db_names)
        col1.write(dbs_to_remove)

        if col1.button('Remove'):
            [st.session_state.extracted_schemas.pop(key, None) for key in dbs_to_remove]
            # map(st.session_state.extracted_schemas.pop, dbs_to_remove)
            col1.info('Remove successfuly')
        
        ### Handle query at col2
        user_question = col2.text_input('Enter your question:')

        ## Retrieve processing to get DB corresponding to the user question
        text_schema = {k: str(v) for k, v in st.session_state.extracted_schemas.items()}
        vector_store = FAISS.from_texts(list(text_schema.values()), embedding=embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 1}) # return only the top chunk.
        retriever_chain = create_retriever_tool(retriever, 'DB_schema_extractor', 'This tool is to give database schema based on queries')

        ## print Query
        if user_question:
            try: 
                # Augment process
                schema = retriever_chain.invoke(user_question)
                formatted_promt = format_promt(schema=schema, query=user_question)

                best_db_index = list(text_schema.values()).index(schema)
                best_db_name = db_names[best_db_index]
                # Generate process
                # try:
                #     final_query = col2.text_input('The generated query:', SQLquery_generater(formatted_promt=formatted_promt))
                # except:
                #     print('Please re-try. Something happen to our LLM.')
                final_query = col2.text_input('The generated query:', SQLquery_generater(formatted_promt=formatted_promt))
                final_DB = col2.selectbox('Appy for database:', db_names, index=db_names.index(best_db_name))

                col2.info('You can adjust the result for your demand')
                
                if col2.button('Apply the query'):
                    try:
                        col2.dataframe(apply_query(default_db_url.format(final_DB), final_query))
                    except RuntimeError as e:
                        col2.error(f'Error applying the query. Please check the SQL code.')
                    
            except RuntimeError as e:
                col2.error(f"Error setting up the language model")
    else:
        st.info('Please Submit Databases')


if __name__ == '__main__':
    main()