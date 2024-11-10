from sqlalchemy import create_engine, inspect, text
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import streamlit as st
import pandas as pd

@st.cache_data
def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)

    # Get list of tables
    tables = inspector.get_table_names()

    schema = {}
    # Loop through each table and print its schema
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        schema[f'Table: {table_name}'] = {f"column: {column['name']}": [f"Type: {column['type']}", f"primary_key: {column['primary_key']}"] for column in columns}
        
    return schema

def apply_query(db_url, query):
    engine = create_engine(db_url)

    with engine.connect() as connection:
        results = list(connection.execute(text(query)))
    return pd.DataFrame(results)

prompt_template = """You are an AI that generates SQL queries from a database schema and a question. Example:
Schema: `Table Student - StudentID (INTEGER, PK), ClassID (INTEGER)`
`Table Class - ClassID (INTEGER, PK), ClassName (TEXT)`

Question: 'How many students are in the Chemistry class?'
Query:
```sql
SELECT count(s.StudentID) as no_student
FROM Student s, Class c
WHERE s.ClassID = c.ClassID AND c.ClassName = 'Chemistry'
```

Using the schema `{schema}`, generate a SQL query for:
{question}

SQL Query:
"""

@st.cache_data
def format_promt(schema, query, prompt_template=prompt_template):
    prompt = PromptTemplate(
        input_variables = ["schema", "question"],
        template = prompt_template,
    )
    return prompt.format(schema=schema, question=query)

model_names = {'gpt2': 'gpt2',
               'falcon-7b': "tiiuae/falcon-7b-instruct"}

@st.cache_data
def SQLquery_generater(formatted_promt, model_name='gpt2'):
    if model_name not in list(model_names.keys()):
        raise ValueError('model is NOT supported')

    # Load the model
    tokenizer = AutoTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Set up a local pipeline
    sql_generator = pipeline(task='text-generation', 
                             model=model, 
                             tokenizer=tokenizer, 
                             max_new_tokens=100, 
                             pad_token_id=50256) # Setting `pad_token_id` to `eos_token_id`:None for open-end generation
    
    llm = HuggingFacePipeline(pipeline=sql_generator)

    # Use the local model with the prompt
    response = llm(formatted_promt, do_sample=True, temperature=0.7)
    return response[len(formatted_promt):].strip() # response_without_context
