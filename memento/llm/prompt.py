PROMPT = """\
You are an expert task processing assistant.
Your task is to analyze the given text and extract structured information.

Instructions:
1. Create a short, descriptive title (max 40 characters)
2. Extract the main text of the tax (exclude links and assignee info) and rewrite it for clarity
3. If you find any link in the text put in the link field
4. If there is @NAME mention, remove @ and set the rest as the assignee
5. If any field doesn't exist in the text, set it to null

{format}

Reminder text to process:
{text}

Output:\
"""
