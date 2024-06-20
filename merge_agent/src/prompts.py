merge_prompt = """
Output json with the 2 keys 'explanation' and 'code'. The first key's value (str) should explain what steps you took to resolve the merge conflicts and why you did so. The second key's value (str) is the merge conflict resolved code. 
Just output the code so that it can be written to a file (.py, .md, etc.) without errors.

Merge conflicted file content:
{file_content}
"""
commit_prompt = """
I want you to act as a GitHub commit message generator.
Summarize the following explanations in 3-10 words. The summary should contain the most important information from each individual declaration.
Do not write any explanations or other words, just reply with the commit message.

"""
