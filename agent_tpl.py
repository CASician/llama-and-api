import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

my_model = "gpt-4o-mini"

# -------- CONFIGURAZIONE --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# URL base del portale TPL
TPL_BASE_URL = "https://www.snap4city.org/superservicemap/api/v1/tpl"

# -------- FUNZIONI API --------
def get_agencies():
    """
    Chiama l'endpoint che restituisce le agenzie di autobus.
    """
    url = f"{TPL_BASE_URL}/agencies"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Mappa delle funzioni che il modello può invocare
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_agencies",
            "description": "Ritorna la lista delle agenzie di autobus TPL.",
            "parameters": { "type": "object", "properties": {} }
        }
    }
]

# -------- AGENTE --------
def agent_loop(user_message: str):
    """
    Invia il messaggio utente al modello. Se il modello
    richiede una tool call, esegue la funzione e rimanda il risultato.
    """
    messages = [
        {"role": "system", "content": "Se necessario puoi chiamare le API TPL per rispondere."},
        {"role": "user", "content": user_message}
    ]

    # Prima risposta del modello
    first = client.chat.completions.create(
        model=my_model,      # poi 'llama-4' con base_url del laboratorio
        messages=messages,
        tools=TOOLS
    )

    choice = first.choices[0]
    # Se non ha chiamato alcuna funzione, ritorna la risposta diretta
    if not choice.message.tool_calls:
        print(choice.message.content)
        return

    # Esegui la/e funzioni richieste
    for tool_call in choice.message.tool_calls:
        if tool_call.function.name == "get_agencies":
            result = get_agencies()
            # Aggiungi il risultato alla conversazione
            messages.append(choice.message)  # output del modello
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    # Seconda chiamata: il modello usa i dati per comporre la risposta finale
    second = client.chat.completions.create(
        model=my_model,
        messages=messages
    )
    print(second.choices[0].message.content)


if __name__ == "__main__":
    # Esempio d'uso
    domanda = "Quali sono le linee di autobus disponibili in Toscana?"
    agent_loop(domanda)
