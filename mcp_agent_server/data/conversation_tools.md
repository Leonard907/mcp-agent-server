Name: set_conv_history
Description: Store the conversation history for later retrieval by other tools.
Parameters:
- conversation: string. The full conversation history to store.
Required: conversation 

Name: summarize
Description: Summarize the current conversation history.
Parameters:
- level: Enum[concise, normal, detailed]. The level of detail to summarize the conversation history.
Required: level