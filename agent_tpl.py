import os
import json
from snap_api import get_agencies, get_bus_lines, get_bus_routes, get_bus_stops
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

models = ["gpt-4o","gpt-4o-mini", "o4-mini", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.1", "gpt-3.5-turbo", "gpt-5-mini"]
my_model = models[3]

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
    },
    {
        "type": "function",
        "function": {
            "name": "get_bus_lines",
            "description": "Returns the bus lines available for a given TPL agency URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agency_url": {
                        "type": "string",
                        "description": "The full agency URL returned by get_agencies (e.g., https://.../agency/ID)."
                    }
                },
                "required": ["agency_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bus_routes",
            "description": "Returns the routes for a bus line of an agency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agency_url": {"type": "string", "description": "Full agency URL."},
                    "line": {"type": "string", "description": "Line name/number."},
                    "geometry": {"type": "boolean", "description": "Include route geometry.", "default": False}
                },
                "required": ["agency_url", "line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bus_stops",
            "description": "Returns the stops for a specific route.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route_url": {"type": "string", "description": "Full route URL."},
                    "geometry": {"type": "boolean", "description": "Include stop geometry.", "default": False}
                },
                "required": ["route_url"]
            }
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
        {"role": "system", "content": (
            "You can call TPL APIs if needed. For TPL queries: "
            "(1) If the user mentions a city/area/operator, first call get_agencies and match by name/city/area; "
            "(2) To list lines, call get_bus_lines(agency_url); "
            "(3) To explore a specific line, call get_bus_routes(agency_url, line, geometry?); "
            "(4) To list stops, call get_bus_stops(route_url, geometry?); "
            "Ask a short clarifying question if any required parameter is ambiguous."
        )}
    ]

    while True:
        try:
            user_message = input("\nYou: ").strip()
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
            function_name = getattr(tool_call.function, "name", None)
            raw_arguments = getattr(tool_call.function, "arguments", None)

            # Parse arguments (OpenAI returns a JSON string)
            if isinstance(raw_arguments, str):
                try:
                    args = json.loads(raw_arguments) if raw_arguments else {}
                except Exception:
                    args = {}
            elif isinstance(raw_arguments, dict):
                args = raw_arguments
            else:
                args = {}

            result_payload = None
            error_message = None

            if function_name == "get_agencies":
                try:
                    result_payload = get_agencies()
                except Exception as e:
                    error_message = f"get_agencies failed: {e}"

            elif function_name == "get_bus_lines":
                agency_url = args.get("agency_url") if isinstance(args, dict) else None
                if not agency_url:
                    error_message = "Missing required 'agency_url' argument."
                else:
                    try:
                        result_payload = get_bus_lines(agency_url=agency_url)
                    except Exception as e:
                        error_message = f"get_bus_lines failed: {e}"
            elif function_name == "get_bus_routes":
                agency_url = args.get("agency_url") if isinstance(args, dict) else None
                line = args.get("line") if isinstance(args, dict) else None
                geometry = bool(args.get("geometry")) if isinstance(args, dict) else False
                if not agency_url or not line:
                    error_message = "Missing required 'agency_url' or 'line' argument."
                else:
                    try:
                        result_payload = get_bus_routes(agency_url=agency_url, line=line, geometry=geometry)
                    except Exception as e:
                        error_message = f"get_bus_routes failed: {e}"

            elif function_name == "get_bus_stops":
                route_url = args.get("route_url") if isinstance(args, dict) else None
                geometry = bool(args.get("geometry")) if isinstance(args, dict) else False
                if not route_url:
                    error_message = "Missing required 'route_url' argument."
                else:
                    try:
                        result_payload = get_bus_stops(route_url=route_url, geometry=geometry)
                    except Exception as e:
                        error_message = f"get_bus_stops failed: {e}"

            else:
                error_message = f"Unknown tool: {function_name}"

            # Always respond with a tool message for each tool_call_id
            if error_message is None:
                content = json.dumps({"ok": True, "data": result_payload})
            else:
                content = json.dumps({"ok": False, "error": error_message})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content
            })

        # Second call: compose the final answer using tool results
        second = client.chat.completions.create(
            model=my_model,
            messages=messages
        )
        assistant_text = second.choices[0].message.content or ""
        print(f"Assistant: {assistant_text}")
        messages.append({"role": "assistant", "content": assistant_text})
