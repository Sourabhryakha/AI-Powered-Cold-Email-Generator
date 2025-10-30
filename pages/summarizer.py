import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

st.title("📧 Email Summarizer")
mail_input = st.text_input("Enter the mail content:", value=" ")
submit_button = st.button("Submit")

if submit_button:
        try:
            llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")
            prompt_extract = PromptTemplate.from_template(
            """
            ### EMAIL CONTENT:
            {mail_input}
            
            ### INSTRUCTION:
            If the `mail_input` is empty, or if they contain random characters that do not form coherent text, do not generate a response. Instead, return the following message: "Please provide a valid "email" content."
            Analyze the email and summarize it effectively. Use JSON format internally to organize the following:
            - The purpose of the email.
            - Key details or important points mentioned.
            - Any action items, requests, or follow-ups required (if any).
            the above three points should be hilighted in output
            Based on this internal JSON structure, generate a well-organized textual summary that can be directly displayed. Ensure the summary is:
            - Concise and to the point.
            - Clearly structured for easy understanding.
            - Suitable for direct presentation to a user.
            
            in the output don't ever mention json 
            write the summary is less than 200 words
            """
            )
            chain_extract = prompt_extract | llm
            res = chain_extract.invoke(input={"mail_input": mail_input})
            st.markdown(f"### Generated Response:\n\n{res.content}")
            # st.code(res.content, language='markdown')
            #st.text_area("Generated Response:", value=res.content, height=300,disabled=True)
        except Exception as e:
            st.error(f"An Error Occurred: {e}")