import json
from typing import Sequence
from mcp_agent_server.utils import *

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

async def serve() -> None:
    server = Server("mcp-agent-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools, _ = get_all_tools()
        return tools

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for time queries and conversation history."""
        result = ""
        try:
            result = execute_tool(name, arguments)

            return [
                TextContent(type="text", text=result)
            ]

        except Exception as e:
            raise ValueError(f"Error processing tool query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)