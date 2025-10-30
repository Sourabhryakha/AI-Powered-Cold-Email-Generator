import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Initialize session state for response
if "generated_response" not in st.session_state:
    st.session_state.generated_response = ""

st.title("📧 Email Response Generator")
mail_input = st.text_input("Enter the mail content:", value=" ")
res_input = st.text_input("Enter the response:", value=" ")
submit_button = st.button("Submit")

if submit_button:
    try:
        llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",
        )
        prompt_extract = PromptTemplate.from_template(
            """
            ### EMAIL RECEIVED:
            {mail_input}

            ### REQUIRED RESPONSE CONTENT:
            {res_input}

            ### INSTRUCTION:
            If the `mail_input` or `res_input` are empty, or if they contain random characters that do not form coherent text, do not generate a response. Instead, return the following message: "Please provide a valid email and response content."
            If the `mail_input` is empty, or if it contain random characters that do not form coherent text, do not generate a response. Instead, return the following message: "Please provide a valid email."
            If the `res_input` is empty, or if they contain random characters that do not form coherent text, do not generate a response. Instead, return the following message: "Please provide a valid response content."
            Otherwise, draft a professional email response to the above email. The response should:
            1. Address the sender politely and professionally based on the context of the received email.
            2. Include the "REQUIRED RESPONSE CONTENT" ({res_input}) as part of the body of the email in a natural and coherent way.
            3. Maintain a professional and formal tone throughout the email.
            4. Ensure clarity, grammatical accuracy, and proper formatting.

            Structure the email as follows:
            - **Subject**: A concise and relevant subject line for the response.
            - **Greeting**: Start with a professional salutation (e.g., "Dear [Name],").
            - **Body**: Incorporate the details from "REQUIRED RESPONSE CONTENT" while addressing the key points from the received email.
            - **Closing**: End with a polite closing statement and a professional sign-off.

            Generate only the final email text without any explanations or preambles.
            """
        )
        chain_extract = prompt_extract | llm
        res = chain_extract.invoke(input={"mail_input": mail_input, "res_input": res_input})
        
        # Save the generated response in session state
        st.session_state.generated_response = res.content
    except Exception as e:
        st.error(f"An Error Occurred: {e}")

# Display the generated response if it exists
if st.session_state.generated_response:
    st.title("Generated Response")
    st.text_area("",value=st.session_state.generated_response, height=400, )

    # Add a copy button
    if st.button("Copy Email"):
        st.session_state.clipboard = st.session_state.generated_response  # Simulate copying to clipboard
        st.success("Email copied to clipboard!")
