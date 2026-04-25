import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chains import Chain
from urllib.parse import urlparse


def is_valid_url(url):
    url = url.strip()
    parsed = urlparse(url)

    if not (parsed.scheme and parsed.netloc):
        return False

    keywords = ["career", "careers", "job", "jobs"]
    return any(keyword in url.lower() for keyword in keywords)


def create_streamlit_app(llm):
    st.title("📧 AI Cold Mail Generator")

    # ---------------------------
    # USER INPUT (IMPORTANT)
    # ---------------------------
    name = st.text_input("Your Name")
    skills = st.text_area("Your Skills (e.g., Python, ML, Web Dev)")
    experience = st.text_area("Your Experience / Projects")

    url_input = st.text_input("Enter a careers/jobs URL:")
    submit_button = st.button("Generate Email")

    # Session state
    if "email" not in st.session_state:
        st.session_state.email = ""

    if submit_button:
        if not name or not skills:
            st.warning("Please fill your name and skills.")
            return

        if not is_valid_url(url_input):
            st.error("Please provide a valid job/careers URL.")
            return

        try:
            # ---------------------------
            # LOAD DATA
            # ---------------------------
            loader = WebBaseLoader([url_input])
            raw_data = loader.load().pop().page_content

            # ---------------------------
            # CHUNKING (IMPORTANT)
            # ---------------------------
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            )
            chunks = splitter.split_text(raw_data)

            # ---------------------------
            # FILTER RELEVANT CHUNKS
            # ---------------------------
            relevant_chunks = [
                c for c in chunks
                if "job" in c.lower() or "career" in c.lower()
            ]

            jobs = []

            for chunk in relevant_chunks[:5]:
                try:
                    extracted = llm.extract_jobs(chunk)
                    jobs.extend(extracted)
                except Exception:
                    continue

            # ---------------------------
            # NO JOB FOUND
            # ---------------------------
            if not jobs:
                st.warning("No job data could be extracted from this page.")
                return

            # ---------------------------
            # USE BEST JOB ONLY
            # ---------------------------
            best_job = jobs[0]

            email = llm.write_mail(
                best_job,
                url_input,
                name,
                skills,
                experience
            )

            st.session_state.email = email

        except Exception as e:
            st.error(f"An Error Occurred: {e}")

    # ---------------------------
    # DISPLAY RESULT
    # ---------------------------
    if st.session_state.email:
        st.text_area("Generated Email", value=st.session_state.email, height=350)

        st.download_button(
            "Download Email",
            st.session_state.email,
            file_name="cold_email.txt"
        )


if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain)

