import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from utils import clean_text
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Validates the URL format and checks for required keywords.
    """
    # Strip trailing spaces from the URL
    url = url.strip()

    # Parse the URL to ensure it has a scheme and netloc
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc):
        return False

    # Check for required keywords
    keywords = ["career", "careers", "job", "jobs"]
    return any(keyword in url.lower() for keyword in keywords)



def create_streamlit_app(llm, clean_text):
    st.title("📧 Cold Mail Generator")

    # Initialize session state variables
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "clipboard" not in st.session_state:
        st.session_state.clipboard = ""

    # Input and submit button
    url_input = st.text_input("Enter a URL:", value=" ")
    submit_button = st.button("Submit")

    if submit_button:
        if not is_valid_url(url_input):
            st.error("Please provide a valid URL containing 'career,' 'careers,' 'job,' or 'jobs.'")
        else:
            try:
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                jobs = llm.extract_jobs(data)
                for job in jobs:
                    st.session_state.email = llm.write_mail(job, url_input)
            except Exception as e:
                st.error(f"An Error Occurred: {e}")

    # Display the generated email if available
    if st.session_state.email:
        st.text_area("Generated Email", value=st.session_state.email, height=400)

        # Copy email button
        if st.button("Copy Email"):
            st.session_state.clipboard = st.session_state.email
            st.success("Email copied to clipboard!")


if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, clean_text)