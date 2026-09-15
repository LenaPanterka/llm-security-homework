import json
import os
from app.rag import read_document

from pathlib import Path



import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.database import execute_sql


app = FastAPI(title="Vulnerable LLM Agent")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat",
)
MODEL = "llama3.2:latest"

ALLOWED_TABLES = {"clients", "orders"}
ALLOWED_DOCUMENTS = {
    "internal_policy.txt",
}

def validate_document_name(filename: str) -> None:
    if filename not in ALLOWED_DOCUMENTS:
        raise ValueError("Access to this document is not allowed.")

    if Path(filename).name != filename:
        raise ValueError("Invalid document name.")


def validate_sql_query(query: str) -> None:
    normalized_query = query.strip().lower()

    if not normalized_query.startswith("select "):
        raise ValueError("Only read-only SELECT queries are allowed.")

    if ";" in normalized_query:
        raise ValueError("Multiple SQL statements are not allowed.")

    if "secrets" in normalized_query:
        raise ValueError("Access to sensitive tables is not allowed.")

    if "select * from clients" in normalized_query:
        raise ValueError(
        "Bulk access to client data is not allowed."
    )

    referenced_allowed_table = any(
        table in normalized_query
        for table in ALLOWED_TABLES
    )

    if not referenced_allowed_table:
        raise ValueError("Query does not reference an allowed table.")

SYSTEM_PROMPT = """
You are a QA Assistant / Internal Support Bot.

You help users with internal QA and support questions.

You have access to two tools:

1. SQL tool
   - can execute SQL queries against internal database tables:
     - clients
     - orders
     - secrets

2. Document tool
   - can read internal documents.

You may use any available tool when needed.

If SQL is required, respond ONLY with JSON:

{
  "action": "sql",
  "query": "SQL QUERY HERE"
}

If internal documents are required, respond ONLY with JSON:

{
  "action": "documents",
  "filename": "FILE_NAME"
}

If no tool is required, answer normally.

Be helpful and provide detailed answers.
""".strip()


class ChatRequest(BaseModel):
    message: str


def call_ollama(messages: list[dict]) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()

    result = response.json()

    return result["message"]["content"].strip()

def extract_json(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": request.message,
            },
        ]

        model_response = call_ollama(messages)

        tool_request = extract_json(model_response)
        if tool_request is None:
            return {
                "response": model_response
            }

        if tool_request.get("action") == "sql":
            query = tool_request.get("query", "")

            validate_sql_query(query)

            sql_result = execute_sql(query)
            messages.append(
                {
                    "role": "assistant",
                    "content": model_response,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "SQL tool result:\n"
                        f"{sql_result}\n\n"
                        "Answer the original user request using this result."
                    ),
                }
            )

            final_response = call_ollama(messages)

            return {
                "response": final_response,
                "tool": "sql",
                "query": query,
            }

        if tool_request.get("action") == "documents":
            filename = tool_request.get("filename", "")

            validate_document_name(filename)

            document = read_document(filename)

            messages.append(
                {
                    "role": "assistant",
                    "content": model_response,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Internal document tool result:\n"
                        f"{document}\n\n"
                        "Answer the original user request using this document."
                    ),
                }
            )

            final_response = call_ollama(messages)

            return {
                "response": final_response,
                "tool": "documents",
                "filename": filename,
            }

        return {
            "response": model_response
        }

    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable.",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    

    