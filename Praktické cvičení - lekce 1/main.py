import json
from openai import OpenAI
from api_key import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

available_functions = {
    "add_numbers": add_numbers,
    "subtract_numbers": subtract_numbers,
    "multiply_numbers": multiply_numbers,
    "divide_numbers": divide_numbers,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Adds two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "subtract_numbers",
            "description": "Subtracts b from a (a - b).",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Minuend"},
                    "b": {"type": "number", "description": "Subtrahend"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Multiplies two numbers (a * b).",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First factor"},
                    "b": {"type": "number", "description": "Second factor"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "divide_numbers",
            "description": "Divides a by b (a / b).",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Dividend"},
                    "b": {"type": "number", "description": "Divisor (non-zero)"},
                },
                "required": ["a", "b"],
            },
        },
    },
]


def main():
    user_prompt = "Vypočítej 12 - 8 a vysvětli postup."

    print("USER:", user_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful math assistant. "
                "If the user clearly wants to COMPUTE something with numbers "
                "(addition, subtraction, multiplication, division), "
                "use the appropriate tool (add_numbers, subtract_numbers, multiply_numbers, divide_numbers). "
                "If the user only asks for an explanation or theory without a concrete calculation, "
                "answer directly without using tools."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]

    # 1) první volání LLM – může si vyžádat tool_calls
    first_response = client.chat.completions.create(
        model="gpt-5.1-chat-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = first_response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"\nMODEL chce zavolat nástroj: {tool_name}({tool_args})")

            if tool_name not in available_functions:
                tool_result = {"error": f"Unknown tool: {tool_name}"}
            else:
                func = available_functions[tool_name]
                try:
                    result = func(**tool_args)
                    tool_result = {"result": result}
                except Exception as e:
                    tool_result = {"error": str(e)}

            print(f"Výsledek nástroje: {tool_result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                }
            )

        # 2) druhé volání LLM – ať z výsledků udělá finální vysvětlení
        second_response = client.chat.completions.create(
            model="gpt-5.1-chat-latest",
            messages=messages,
        )
        final_answer = second_response.choices[0].message.content
        print("\nASSISTANT (s použitím nástroje):")
        print(final_answer)

    else:
        final_answer = response_message.content
        print("\nASSISTANT (bez nástroje):")
        print(final_answer)


if __name__ == "__main__":
    main()

