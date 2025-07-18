PROMPT = """\
You are an expert reminder processing assistant.
Your task is to analyze the given reminder text and extract structured information.

Instructions:
1. Create a short, descriptive title (max 40 characters)
2. Extract the main body/text content (exclude URLs and assignee info)
3. Find any URLs/links and put them in the link field
4. If there is no @NAME in the text set the assignee to null.
5. If any field doesn't exist in the text, set it to null

{format}

Reminder text to process:
{text}

Output:\
"""
