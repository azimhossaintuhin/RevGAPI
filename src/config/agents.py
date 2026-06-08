from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from decouple import config
from src.schemas.Output import AgentOutput
google_api_key = config("GOOGLE_API_KEY")

llm: GoogleGenerativeAI = GoogleGenerativeAI(model="gemini-3.1-flash-lite",api_key=google_api_key)

parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=AgentOutput)
format_instructions: str = parser.get_format_instructions()

system_message_template: str = """
You are a helpful tool that can help with comment and  feedback analysis. You will always check the sentiment of the comment   also  give the  summary, pros, cons, action items, suggestions, customer_repeats, confidence_score , feedback_language, translation.
You will always return the output in the following format:
{format_instructions}
"""

template = ChatPromptTemplate.from_messages([
    ("system", system_message_template),
    ("user", "{input}"),
]).partial(format_instructions=format_instructions)


chain = template | llm | parser



