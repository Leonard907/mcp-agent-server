import re
from typing import List, Dict, Any, Tuple
from mcp.types import Tool
from openai import OpenAI
import os
from dotenv import load_dotenv
from prompts.prompt_utils import load_system_prompt, load_user_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# Handling General Tool Calling using LLMs
def parse_tools(file_path: str = "data/tools.md") -> List[Tool]:
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
    tools = parse_tools()
    
    names_dict = {tool.name: tool for tool in tools}
    return tools, names_dict

# Tool Execution
def execute_tool(name: str, arguments: dict) -> str:
    conv_history = arguments.get("conversation_history", "")
    if conv_history:
        del arguments["conversation_history"]

    all_tools, names_dict = get_all_tools()
    target_tool = names_dict.get(name)
    if not target_tool:
        return f"Tool {name} not found"
    
    parameters_desc_string = "\n".join(
        [f"- {k}: {v['description']}" for k,v in target_tool.inputSchema["properties"].items()]
    )

    parameters_string = "\n".join(
        [f"- {k}: {v}" for k,v in arguments.items()]
    )

    system_prompt = load_system_prompt(task_description=target_tool.description, task_parameters=parameters_desc_string)
    user_prompt = load_user_prompt(task_description=target_tool.description, task_parameters=parameters_string)

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content
