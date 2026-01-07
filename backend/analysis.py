from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import os

# Define Output Structure
class AnalysisResult(BaseModel):
    grammar_corrected: str = Field(description="The text with all grammar errors corrected")
    grammar_errors: list[str] = Field(description="List of specific grammar errors found. Empty if none.")
    ai_likelihood_score: int = Field(description="Score from 0 to 100 indicating probability of AI generation")
    ai_likelihood_reasoning: str = Field(description="Explanation for the AI score")

# Initialize LLM (Groq)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
parser = JsonOutputParser(pydantic_object=AnalysisResult)

template = """You are an expert linguistic analyst. 
Analyze the following text for:
1. Grammar and spelling errors. If none, return empty list.
2. Stylometric features to estimate if it was written by an AI.

Text to Analyze:
{text}

{format_instructions}
"""

prompt = ChatPromptTemplate.from_template(
    template,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser

async def analyze_text(text: str):
    if not os.environ.get("GROQ_API_KEY"):
        return {
            "grammar_corrected": text,
            "grammar_errors": ["Error: Groq API Key missing"],
            "ai_likelihood_score": 0,
            "ai_likelihood_reasoning": "Analysis failed due to missing key."
        }
    
    try:
        result = chain.invoke({"text": text})
        return result
    except Exception as e:
        # Fallback if parsing fails or LLM errors
        print(f"Analysis Error: {e}")
        return {
            "grammar_corrected": text,
            "grammar_errors": [f"Analysis failed: {str(e)}"],
            "ai_likelihood_score": 0,
            "ai_likelihood_reasoning": "Could not process text."
        }
