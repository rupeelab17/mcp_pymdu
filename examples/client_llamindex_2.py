# https://medium.com/@pedroazevedo6/build-llamaindex-agents-with-mcp-connector-69df32d95508

import asyncio
import dotenv
from httpcore import ConnectError

from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context

dotenv.load_dotenv()

# 1. Instanciation du LLM
llm = Ollama(model="devstral:24b", request_timeout=120.0)


# 2. Fonction pour créer l’agent à partir du spec MCP
async def get_agent_from_spec(mcp_spec: McpToolSpec) -> FunctionAgent:
    try:
        tools = await mcp_spec.to_tool_list_async()
    except ConnectError as e:
        print(f"❌ Impossible de joindre le serveur MCP : {e}")
        return  # ou gérez la reprise selon votre logique

    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with Our Database software.",
        tools=tools,
        llm=llm,
        system_prompt=(
            "You are an AI assistant for Tool Calling.\n"
            "Before you help a user, you need to work with tools to interact with Our Database."
        ),
    )
    return agent


# 3. Handler asynchrone pour un message utilisateur
async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    context: Context,
    verbose: bool = False,
) -> str:
    handler = agent.run(message_content, ctx=context)
    async for event in handler.stream_events():
        if verbose:
            if isinstance(event, ToolCall):
                print(f"> Calling tool {event.tool_name} with {event.tool_kwargs}")
            elif isinstance(event, ToolCallResult):
                print(f"> Tool {event.tool_name} returned {event.tool_output!r}")
    result = await handler
    return str(result)


# 4. Boucle principale asynchrone
async def main():
    # 4.1 Préparation du client MCP et du spec
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_spec = McpToolSpec(client=mcp_client)

    # 4.2 Création de l’agent et du contexte
    agent = await get_agent_from_spec(mcp_spec)
    agent_context = Context(agent)

    print("🤖 Agent ready! Tapez 'exit' pour quitter.")
    # 4.3 Boucle de conversation
    while True:
        user_input = await asyncio.to_thread(input, "You: ")
        if user_input.strip().lower() == "exit":
            print("👋 Au revoir !")
            break

        # 4.4 Envoi du message et affichage de la réponse
        response = await handle_user_message(
            user_input, agent, agent_context, verbose=True
        )
        print("Agent:", response)


if __name__ == "__main__":
    asyncio.run(main())
