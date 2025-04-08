import json
from typing import Sequence
from utils import *

from zoneinfo import ZoneInfo
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError
from conversation import conversation_server
from utils import *

async def serve() -> None:
    server = Server("mcp-agent-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools, _, _ = get_all_tools()
        return tools

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for time queries and conversation history."""
        result = ""
        try:
            match name:
                case "set_conv_history":
                    conversation = arguments.get("conversation")
                    if not conversation:
                        raise ValueError("Missing required argument: conversation")
                    
                    result = conversation_server.set_conversation_history(conversation)
                
                case _:
                    result = execute_tool(name, arguments)

            return [
                TextContent(type="text", text=result)
            ]

        except Exception as e:
            raise ValueError(f"Error processing tool query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)