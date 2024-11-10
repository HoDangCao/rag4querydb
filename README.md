# RAG for Database without exposing Data: Text to SQL

## Table of Contents
- [What have been done in this project?](#1-what-have-been-done-in-this-project)
- [Demo](#2-demo)
- [How to run app](#3-how-to-run-app)

## 1. **What have been done in this project?**
Build a websites that allows
- Uploading databases.
- Returning SQL code and result tables corresponding to user queries within few seconds.
- Ensuring data security without feeding data to LLMs.

## 2. **Demo**

<img src='rag4query_demo.gif' width=500>

- The user will upload files at the side bar, then click `Submit & Process`.
- The user can type some questions at the input cell and press `Enter`, then the website will return the corresponding information.

## 3. **How to run app**
- step 0: open cmd/terminal at anywhere you wanna place the app.
- step 1: clone this repository `git clone https://github.com/HoDangCao/rag4querydb.git`
- step 2: run `cd ./rag4querydb`
- step 3: run `pip install -r requiments.txt` 
- step 4: run `streamlit run app.py`
- step 5: Let's experience our website!!!
