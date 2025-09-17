## Prototype for Distributed Systems thesis

The purpose of this project is to create an Agentic RAG capable of using the Snap4City API.

How to run:
- Create a `.env` with `OPENAI_API_KEY=...`.
- Install dependencies: `pip install -r requirements.txt`.
- Start the chat: `python main.py` and type your questions. Type `exit` or `quit` to leave.

Capabilities:
- Understands questions about TPL agencies and can fetch them from the API.
- Can fetch bus lines for a specific agency by first identifying the agency and then calling `bus-lines?agency=AGENCY_URL`.
 - Can fetch routes for a specific line via `bus-routes?agency=AGENCY_URL&line=LINE[&geometry=true]`.
 - Can fetch stops for a specific route via `bus-stops?route=ROUTE_URL[&geometry=true]`.
