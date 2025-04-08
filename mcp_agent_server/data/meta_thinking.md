Name: plan
Description: Generate a detailed plan to solve the given problem.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- problem: string. Description of the problem to solve if read_history is false.
Required: read_history

Name: analysis
Description: Analyze the current solution to locate key information and identify unfinished goals.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- solution: string. Current solution if read_history is false.
Required: read_history

Name: critic
Description: Review the current solution and provide constructive feedback for improvement.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- solution: string. Current solution if read_history is false.
Required: read_history

Name: enhance
Description: Devise a detailed strategy to enhance the current solution.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- solution: string. Current solution if read_history is false.
Required: read_history

Name: pivot
Description: Generate a different plan to solve the problem.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- problem: string. Description of the problem to solve if read_history is false.
- solution: string. Current solution if read_history is false.
Required: read_history

Name: verify
Description: Verify the correctness of the current solution.
Parameters:
- read_history: boolean. Whether to read the history of the conversation. If true, the tool will automatically read the conversation history as input.
- solution: string. Current solution if read_history is false.
Required: read_history

