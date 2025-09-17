import os
from snap_api import get_agencies
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

my_model = "gpt-4o-mini"

# -------- CONFIGURATION --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Map of functions the model can invoke
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_agencies",
            "description": "Returns the list of public transport (TPL) bus agencies.",
            "parameters": { "type": "object", "properties": {} }
        }
    }
]

# -------- AGENT --------
def agent_loop():
    """
    Start an interactive conversational loop. Each turn it:
    - reads the user's input,
    - sends the context to the model with available tools,
    - executes any requested tool calls,
    - prints the response and preserves the conversation memory.
    Type 'exit' or 'quit' to terminate.
    """
    messages = [
        {"role": "system", "content": "If needed you can call the TPL APIs to answer."}
    ]

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        messages.append({"role": "user", "content": user_message})

        # First call: the model may decide to use tools
        first = client.chat.completions.create(
            model=my_model,
            messages=messages,
            tools=TOOLS
        )

        choice = first.choices[0]

        # If there are no tool calls, respond directly and remember it
        if not choice.message.tool_calls:
            assistant_text = choice.message.content or ""
            print(f"Assistant: {assistant_text}")
            messages.append({"role": "assistant", "content": assistant_text})
            continue

        # Execute functions requested by the model
        messages.append(choice.message)  # include message with tool_calls
        for tool_call in choice.message.tool_calls:
            if tool_call.function.name == "get_agencies":
                result = get_agencies()
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        # Second call: compose the final answer using tool results
        second = client.chat.completions.create(
            model=my_model,
            messages=messages
        )
        assistant_text = second.choices[0].message.content or ""
        print(f"Assistant: {assistant_text}")
        messages.append({"role": "assistant", "content": assistant_text})
