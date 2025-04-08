import re
from typing import List, Dict, Any, Tuple
from enum import Enum
from mcp.types import Tool
from openai import OpenAI
from prompts.prompt_utils import build_meta_thinking_prompts

client = OpenAI()

# Handling Conversation History for Tool Calling
class ConversationTools(Enum):
    SET_CONV_HISTORY = "set_conv_history"

class ConversationServer:
    def __init__(self):
        self.question = ""
        self.conversation_history = None
        
    def set_conversation_history(self, history: str):
        self.conversation_history = history
        return {"status": "success", "message": "Conversation history stored successfully"}
    
    def set_question(self, question: str):
        self.question = question
        return {"status": "success", "message": "Question stored successfully"}
        
    def get_conversation_history(self):
        if self.conversation_history is None:
            return {"status": "error", "message": "No conversation history available"}
        return {"conversation": self.conversation_history}
    
    def get_question(self):
        return {"question": self.question}

conversation_server = ConversationServer()

# Handling General Tool Calling using LLMs
def parse_tools(file_path: str = "data/meta_thinking.md") -> List[Tool]:
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Meta thinking file not found at: {file_path}")
    
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
                    if "boolean" in param_desc:
                        param_type = "boolean"
                    
                    params[param_name] = {
                        "type": param_type,
                        "description": param_desc
                    }
            
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

def get_all_tools() -> Tuple[List[Tool], List[str], List[str]]:
    meta_thinking_tools = parse_tools(file_path="data/meta_thinking.md")
    problem_solving_tools = parse_tools(file_path="data/problem_solving.md") 
    conversation_tools = parse_tools(file_path="data/conversation_tools.md")
    
    meta_thinking_names_dict = {tool.name: tool for tool in meta_thinking_tools}
    problem_solving_names_dict = {tool.name: tool for tool in problem_solving_tools}
    
    return (
        meta_thinking_tools + problem_solving_tools + conversation_tools,
        meta_thinking_names_dict,
        problem_solving_names_dict,
    )

def process_meta_thinking_tool(name: str, arguments: dict, tool: Tool) -> str:
    system_prompt, user_prompt = build_meta_thinking_prompts(arguments, tool)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def process_problem_solving_tool(name: str, arguments: dict) -> str:
    pass

# Tool Execution
def execute_tool(name: str, arguments: dict) -> str:
    all_tools, meta_thinking_names_dict, problem_solving_names_dict = get_all_tools()
    if name in meta_thinking_names_dict:
        return process_meta_thinking_tool(name, arguments, meta_thinking_names_dict[name])
    return "To be implemented"

if __name__ == "__main__":
    # Test the function
    tools = parse_tools()
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Schema: {tool.inputSchema}")
        print("---")
