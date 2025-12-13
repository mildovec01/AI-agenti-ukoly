import os, json
from dotenv import load_dotenv
from openai import OpenAI

from db import init_db
from tools import get_weather, save_note, search_notes

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Zjistí aktuální počasí pro zadané město.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Název města, např. 'Sokolov'"},
            },
            "required": ["city"]
        }
    },
    {
        "type": "function",
        "name": "save_note",
        "description": "Uloží poznámku do databáze (SQLite).",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["title", "content"]
        }
    },
    {
        "type": "function",
        "name": "search_notes",
        "description": "Vyhledá poznámky v databázi (SQLite).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"]
        }
    },
]


def call_tool(name: str, args: dict):
    if name == "get_weather":
        return get_weather(**args)
    if name == "save_note":
        return save_note(**args)
    if name == "search_notes":
        return search_notes(**args)
    return {"error": f"Unknown tool: {name}"}

def run_turn(messages):
    resp = client.responses.create(
        model="gpt-5-mini",
        input=messages,
        tools=TOOLS,
    )


    while True:
        tool_calls = [x for x in resp.output if getattr(x, "type", None) == "function_call"]
        if not tool_calls:
            break

        tool_outputs = []
        for tc in tool_calls:
            name = getattr(tc, "name", None)
            arguments = getattr(tc, "arguments", "{}") or "{}"
            args = json.loads(arguments)

            print(f"[tool] {name}({args})")
            result = call_tool(name, args)

            cid = getattr(tc, "call_id", None) or getattr(tc, "id", None)

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": cid,
                "output": json.dumps(result, ensure_ascii=False)
            })

        resp = client.responses.create(
            model="gpt-5-mini",
            previous_response_id=resp.id,
            input=tool_outputs,
            tools=TOOLS,
        )

    text = getattr(resp, "output_text", None)
    if not text:
        for item in resp.output:
            if getattr(item, "type", None) == "message":
                text = item.content[0].text
                break

    return text or "(no output)"


def main():
    init_db()
    print("Agent ready. Napiš dotaz. (exit = konec)\n")

    messages = [
        {"role": "system", "content":
            "Jsi užitečný agent. Když je to vhodné, používej nástroje get_weather, save_note, search_notes. "
            "Poznámky používej jako znalostní bázi. Odpovídej česky, stručně a věcně."
        }
    ]

    while True:
        user = input("Ty -> ").strip()
        if user.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user})
        answer = run_turn(messages)
        print(f"\nAgent -> {answer}\n")
        messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
