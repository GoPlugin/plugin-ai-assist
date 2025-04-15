from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph,END
from typing import TypedDict
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(title="AI Plugin Assist API")

# Define request body model
class QueryRequest(BaseModel):
    query: str

# Define response model
class QueryResponse(BaseModel):
    response: str

# Read llms.txt file
try:
    with open("llms.txt","r") as file:
        context = file.read()
except FileNotFoundError:
    raise HTTPException(status_code=500,detail="llms.txt file not found")

context = context[:128000]  # Limit to ~10k characters

# Set up OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise HTTPException(status_code=500,detail="OPENAI_API_KEY environment variable not set")

# Initialize OpenAI model
llm = OpenAI(api_key=openai_api_key)

print("llm:::",llm)
# Define prompt template
template = """
You are a helpful assitant for Plugin EcoSystem. Use the following context to answer the user's query. If the query is unrelated, respond appropriately.

Context: {context}

User Query: {query}

Answer:
"""
prompt = PromptTemplate(input_variables=["context","query"],template=template)

# Define the state for LangGraph
class ChatbotState(TypedDict):
    query: str
    context: str
    response: str

# Define the node function for processing the query
def process_query(state: ChatbotState) -> ChatbotState:
    print("process_query:::")
    try:
        formatted_prompt = prompt.format(context=state["context"], query=state["query"])
        response = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        print("response:::", response)
        return {
            "response": response.choices[0].message.content.strip(),
            "query": state["query"],
            "context": state["context"]
        }
    except Exception as e:
        print(f"Error in process_query: {e}")
        return {
            "response": "Sorry, an error occurred while processing your query.",
            "query": state.get("query", ""),
            "context": state.get("context", "")
        }


# Build the LangGraph workflow
workflow = StateGraph(ChatbotState)
workflow.add_node("process_query",process_query)
workflow.set_entry_point("process_query")
workflow.add_edge("process_query",END)
chatbot_graph = workflow.compile()

# API endpoint to handle queries
@app.post("/query",response_model=QueryResponse)
async def get_response(request: QueryRequest):
    try:
        # Run the LangGraph workflow
        initial_state = {"query": request.query,"context": context,"response": ""}
        result = chatbot_graph.invoke(initial_state)
        print("result:::")
        return {"response": result["response"]}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error processing query: {str(e)}")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "AI Plugin Assist API is running"}