from jinja2 import Environment, FileSystemLoader
from mcp.types import Tool
from mcp_agent_server.conversation import conversation_server
import os

# Getting the System Prompt Template
def load_system_prompt(**kwargs) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir)))
    template = env.get_template("meta_thinking_system.jinja")
    return template.render(**kwargs)

def build_meta_thinking_prompts(name: str, arguments: dict, tool: Tool) -> str:
    # Build the system prompt
    read_history = arguments.get("read_history", False)
    if read_history:
        system_prompt = load_system_prompt(task_description=tool.description, read_history=True)
    else:
        system_prompt = load_system_prompt(task_description=tool.description, read_history=False, problem_background=conversation_server.get_question())
    
    # Build the user prompt
    user_prompt = ""
    if read_history:
        user_prompt = f"Conversation History:\n\n{conversation_server.get_conversation_history()}"
    else:
        problem = arguments.get("problem", "")
        solution = arguments.get("solution", "")
        if problem:
            user_prompt += f"Problem to solve:\n\n{problem}"
        if solution:
            user_prompt += ("\n\n" if user_prompt else "") + f"Current Solution:\n\n{solution}"
    
    return system_prompt, user_prompt

def build_conversation_prompts(name: str, arguments: dict, tool: Tool) -> str:
    user_prompt = ""
    if name == "summarize":
        system_prompt = load_system_prompt(task_description=tool.description, read_history=True, need_background=False)
        level = arguments.get("level", "normal")
        conversation_history = arguments.get("conversation_history", "")
        instruction = arguments.get("instruction", "")
        user_prompt = f"Produce a {level} summary of the following conversation:\n\n{conversation_history}"
        if instruction:
            user_prompt += f"\n\nFocus on the following aspect when producing the summary: {instruction}"
    return system_prompt, user_prompt