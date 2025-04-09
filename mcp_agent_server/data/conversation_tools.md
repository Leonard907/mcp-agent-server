Name: summarize
Description: Summarize the current conversation history.
Parameters:
- level: Enum[concise, normal, detailed]. The level of detail to summarize the conversation history.
- conversation_history: string. The full conversation history to summarize. You should always leave this blank as the conversation will be automatically retrieved after the tool is called.
Required: level