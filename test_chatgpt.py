import json
from pathlib import Path
from dataclasses import dataclass
from fastmcp import FastMCP

@dataclass
class Record:
    id: str
    title: str
    text: str
    metadata: dict

def create_server(
    records_path: Path | str,
    name: str | None = None,
    instructions: str | None = None,
) -> FastMCP:
    """Create a FastMCP server that can search and fetch records from a JSON file."""
    records = json.loads(Path(records_path).read_text())

    RECORDS = [Record(**r) for r in records]
    LOOKUP = {r.id: r for r in RECORDS}

    mcp = FastMCP(name=name or "Deep Research MCP", instructions=instructions)

    @mcp.tool()
    async def search(query: str):
        """
        Simple unranked keyword search across title, text, and metadata.
        Searches for any of the query terms in the record content.
        Returns a list of matching record IDs for ChatGPT to fetch.
        """
        toks = query.lower().split()
        ids = []
        for r in RECORDS:
            record_txt = " ".join(
                [r.title, r.text, " ".join(r.metadata.values())]
            ).lower()
            if any(t in record_txt for t in toks):
                ids.append(r.id)

        return {"ids": ids}

    @mcp.tool()
    async def fetch(id: str):
        """
        Fetch a record by ID.
        Returns the complete record data for ChatGPT to analyze and cite.
        """
        if id not in LOOKUP:
            raise ValueError(f"Unknown record ID: {id}")
        return LOOKUP[id]

    return mcp

if __name__ == "__main__":
    mcp = create_server("records.json")
    mcp.run(transport="http", port=8000)

