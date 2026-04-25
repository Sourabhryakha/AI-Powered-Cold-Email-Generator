import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()


class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )

    # -------------------------------
    # JOB EXTRACTION
    # -------------------------------
    def extract_jobs(self, text):
        prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT:
        {page_data}

        ### INSTRUCTION:
        Extract ALL job postings from the text.

        Each job MUST include:
        - role (job title)
        - experience (if not found, write "Not specified")
        - skills (list, if not found return [])
        - description (short summary)

        IMPORTANT RULES:
        - If no jobs found → return []
        - Return ONLY JSON
        - Do NOT include explanation

        ### OUTPUT FORMAT:
        [
          {{
            "role": "",
            "experience": "",
            "skills": [],
            "description": ""
          }}
        ]
        """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke({"page_data": text})

        try:
            json_parser = JsonOutputParser()
            parsed = json_parser.parse(res.content)
        except OutputParserException:
            return []  # safer than crashing

        return parsed if isinstance(parsed, list) else [parsed]

    # -------------------------------
    # EMAIL GENERATION (PERSONALIZED)
    # -------------------------------
    def write_mail(self, job, url_input, name, skills, experience):
        prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}

        ### USER PROFILE:
        Name: {name}
        Skills: {skills}
        Experience: {experience}

        ### INSTRUCTION:
        Write a highly personalized cold email for this job.

        STRICT RULES:
        - Do NOT invent fake experience
        - Use ONLY the provided user data
        - Keep it realistic for a student/fresher
        - Length: 150–250 words
        - Make it human-like, not robotic

        Start with: Respected Sir

        Include:
        - Why you are interested
        - How your skills match
        - 1 small proof (project/skill)

        ### OUTPUT:
        Subject: ...
        
        Email:
        ...
        """
        )

        chain_email = prompt_email | self.llm

        res = chain_email.invoke({
            "job_description": str(job),
            "url_input": url_input,
            "name": name,
            "skills": skills,
            "experience": experience
        })

        return res.content


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))

