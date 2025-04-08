from jinja2 import Template, Environment, FileSystemLoader
from mcp.types import Tool
from utils import conversation_server

# Getting the System Prompt Template
def load_system_prompt(**kwargs) -> str:
    env = Environment(loader=FileSystemLoader("prompts"))
    template = env.get_template("meta_thinking_system.jinja")
    return template.render(**kwargs)

def build_meta_thinking_prompts(arguments: dict, tool: Tool) -> str:
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
