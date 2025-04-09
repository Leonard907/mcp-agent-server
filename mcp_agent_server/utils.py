import re
from typing import List, Dict, Any, Tuple
from enum import Enum
from mcp.types import Tool
from openai import OpenAI
from mcp_agent_server.prompts.prompt_utils import build_meta_thinking_prompts, build_conversation_prompts
from mcp_agent_server.conversation import conversation_server
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# Handling General Tool Calling using LLMs
def parse_tools(file_path: str = "data/meta_thinking.md") -> List[Tool]:
    try:
        # Handle absolute paths
        if os.path.isabs(file_path):
            full_path = file_path
        else:
            # For relative paths, join with the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Check if the file_path starts with the package name, if so remove it from the path
            if file_path.startswith("mcp_agent_server/"):
                file_path = file_path[len("mcp_agent_server/"):]
            full_path = os.path.join(current_dir, file_path)
        
        with open(full_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        raise FileNotFoundError(f"Meta thinking file not found at: {full_path}. Current directory: {current_dir}")
    
    # Split content by tool definitions (each starts with "Name:")
    tool_sections = re.split(r'(?=Name:)', content)
    tools = []
    
    for section in tool_sections:
        if not section.strip():
            continue
            
        # Extract tool properties using regex
        name_match = re.search(r'Name:\s*(\w+)', section)
        description_match = re.search(r'Description:\s*(.+?)(?=\n\w+:|$)', section, re.DOTALL)
        
        if not (name_match and description_match):
            continue
            
        name = name_match.group(1).strip().lower()
        description = description_match.group(1).strip()
        
        # Parse parameters
        params: Dict[str, Dict[str, Any]] = {}
        required_params = []
        
        param_section = re.search(r'Parameters:(.*?)(?=\n\w+:|$)', section, re.DOTALL)
        if param_section:
            param_lines = param_section.group(1).strip().split('\n')
            for line in param_lines:
                if line.strip() and ':' in line:
                    param_parts = line.split(':', 1)
                    param_name = param_parts[0].strip('- ')
                    param_desc = param_parts[1].strip()
                    
                    # Extract param type if it exists in the description
                    param_type = "string"  # Default type
                    param_data = {"description": param_desc}
                    
                    if "boolean" in param_desc:
                        param_type = "boolean"
                    
                    # Check for Enum type
                    enum_match = re.search(r'Enum\[(.*?)\]', param_desc)
                    if enum_match:
                        param_type = "string"
                        # Extract enum values
                        enum_values = [val.strip() for val in enum_match.group(1).split(',')]
                        param_data["enum"] = enum_values
                    
                    param_data["type"] = param_type
                    params[param_name] = param_data
            
            # Check for required parameters
            required_match = re.search(r'Required:\s*(.+?)(?=\n\w+:|$)', section, re.DOTALL)
            if required_match:
                required_params = [p.strip() for p in required_match.group(1).split(',')]
        
        # Create and add the Tool object
        tool = Tool(
            name=name,
            description=description,
            inputSchema={
                "type": "object",
                "properties": params,
                "required": required_params
            }
        )
        
        tools.append(tool)
    
    return tools

def get_all_tools() -> Tuple[List[Tool], Dict[str, Tool], Dict[str, Tool], Dict[str, Tool]]:
    meta_thinking_tools = parse_tools(file_path="data/meta_thinking.md")
    problem_solving_tools = parse_tools(file_path="data/problem_solving.md") 
    conversation_tools = parse_tools(file_path="data/conversation_tools.md")
    
    meta_thinking_names_dict = {tool.name: tool for tool in meta_thinking_tools}
    problem_solving_names_dict = {tool.name: tool for tool in problem_solving_tools}
    conversation_names_dict = {tool.name: tool for tool in conversation_tools}

    all_tools = meta_thinking_tools + problem_solving_tools + [
        tool for tool in conversation_tools if tool.name != "set_conv_history"
    ]

    return (
        conversation_tools,
        meta_thinking_names_dict,
        problem_solving_names_dict,
        conversation_names_dict
    )

def process_meta_thinking_tool(name: str, arguments: dict, tool: Tool) -> str:
    system_prompt, user_prompt = build_meta_thinking_prompts(arguments, tool)
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def process_problem_solving_tool(name: str, arguments: dict, tool: Tool) -> str:
    return "Problem solving output"

def process_conversation_tool(name: str, arguments: dict, tool: Tool) -> str:
    if name == "set_conv_history":
        conversation_server.set_conversation_history(arguments["conversation"])
        return "Conversation history set"
    system_prompt, user_prompt = build_conversation_prompts(name, arguments, tool)
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Tool Execution
def execute_tool(name: str, arguments: dict) -> str:
    all_tools, meta_thinking_names_dict, problem_solving_names_dict, conversation_names_dict = get_all_tools()
    if name in meta_thinking_names_dict:
        return process_meta_thinking_tool(name, arguments, meta_thinking_names_dict[name])
    elif name in problem_solving_names_dict:
        return process_problem_solving_tool(name, arguments, problem_solving_names_dict[name])
    elif name in conversation_names_dict:
        return process_conversation_tool(name, arguments, conversation_names_dict[name])
    return "To be implemented"

if __name__ == "__main__":
    # Test the function
    tools = parse_tools()
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Schema: {tool.inputSchema}")
        print("---")
