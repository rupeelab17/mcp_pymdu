import asyncio
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent

# Connect to the MCP server
mcp_client = BasicMCPClient("http://localhost:8000/sse")
mcp_tool_spec = McpToolSpec(
    client=mcp_client,
    # Optional: Filter the tools by name
    # allowed_tools=["get_bbox_area", "pymdu_lcz_to_image"],
)

tools = mcp_tool_spec.to_tool_list()

# Create an agent
llm = Ollama(model="devstral:24b", request_timeout=120.0)

agent = FunctionAgent(
    tools=tools,
    llm=llm,
    system_prompt="You are an agent that knows how to build agents in LlamaIndex.",
)


async def run_agent():
    response = await agent.run(
        "Affiche Local Climate Zone de la Rochelle Centre pour 4km2"
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(run_agent())
