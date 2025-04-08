Name: python
Description: Write python code to solve the given problem.
Parameters:
- problem: string. Description of the problem to solve.
Required: problem

Name: unix
Description: Write unix commands to solve the given problem.
Parameters:
- problem: string, description of the problem to solve.
Required: problem

Name: math
Description: Solve the given mathematical problem showing step-by-step work.
Parameters:
- problem: string. Description of the mathematical problem to solve.
Required: problem

Name: debug
Description: Debug the given code and identify the issue with detailed explanation.
Parameters:
- code: string. The code snippet with the bug.
- error_message: string. The error message or unexpected behavior description.
Required: code

Name: code_review
Description: Review the provided code and suggest improvements.
Parameters:
- code: string. The code snippet to review.
Required: code

Name: explain_concept
Description: Explain the given concept in a clear and comprehensive manner.
Parameters:
- concept: string. The concept to be explained.
Required: concept

Name: data_analysis
Description: Analyze the provided data and derive insights or patterns.
Parameters:
- data: string. The data to be analyzed or a description of the dataset.
- analysis_type: string. The type of analysis to perform (e.g., statistical, exploratory, predictive).
Required: data, analysis_type 