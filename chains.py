import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job,url_input):
        prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}
        ### URL INPUT:
        {url_input}
        ### INSTRUCTION:
        If the `url_input` does not contain words like "career," "careers," "job," or "jobs," or if it contains random characters that do not form a valid URL, do not generate a response. Instead, return the following message: "Please provide a valid URL."

        Write a subject and a professional cold email. Ensure the email is:
        - No longer than 500 words.
        - Tailored to the job description provided.
        - Polished, concise, and engaging.
        - Focused on highlighting relevant skills, achievements, and enthusiasm for the role.

        You are [Your Name], a motivated jobseeker actively seeking opportunities aligned with your skills and experience. Highlight your most relevant accomplishments and clearly demonstrate how they align with the job requirements.

        Start with the salutation "Respected Sir" and avoid any preamble or unrelated text.

        ### EMAIL:
        """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job),"url_input":url_input})
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))