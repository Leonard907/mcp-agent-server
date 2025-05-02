from jinja2 import Environment, FileSystemLoader
import os

# Getting the System Prompt Template
def load_system_prompt(task_description, task_parameters, conversation_history=None) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir)))
    template = env.get_template("agent_prompt.jinja")
    if conversation_history:
        return template.render(task_description=task_description, task_parameters=task_parameters, read_history=True, conversation_history=conversation_history)
    else:
        return template.render(task_description=task_description, task_parameters=task_parameters, read_history=False)

def load_user_prompt(task_description, task_parameters) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir)))
    template = env.get_template("user_prompt.jinja")
    return template.render(task_description=task_description, task_parameters=task_parameters)