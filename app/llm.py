from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import os

load_dotenv()

def generate_ai_output(model_name, system_prompt, user_context):
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{context}")
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"context": user_context})
