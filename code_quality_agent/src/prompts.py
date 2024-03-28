lint_prompt = """
You will get two sections of code separated by ####. The first section \
contains source code that can be improved. A linter has already been used for \
this code to improve the code quality. The second code section contains the \
linter's suggestions for improving the code. Based on the linter's suggestions, \
return the improved source code. Try to improve the code quality independently \
and don't necessarily implement the linter suggestions 1:1.

Proceed as follows:
1. Analyze the source code and identify traditional coding \
conventions in the code.
2. Formulate a plan to improve the code quality.
3. Evaluate the linter suggestions and compare them with your plan.
4. Apply changes that improve code quality and maintain the current coding \
convention if one is found. Do not add placeholders in your code, even if the \
linter recommendations suggest it. The source code must be compilable or \
interpretable. Avoid creating a package structure that would require placeholders. \
Make sure to use the insights from points 2. and 3..
5. Ensure that the solution you found is compilable or interpretable, and does not \
contain placeholders or incomplete package structures.
6. Return a json object with 2 keys, "improved_source_code" and "explanation". \

####
source code:
{source_code}
####
linter suggestions:
{linter_suggestions}
####
"""

docs_prompt = """
# Problem Statement:
We have a collection of codebases in various programming languages that are \
not adequately documented. Our goal is to improve the documentation of these \
codebases to enhance the maintainability and understandability of the code. We \
would like you to assist us in generating docstrings for the undocumented or \
poorly documented code.
Return a json object with 2 keys, "documented_source_code" and "explanation".

## Programming Languages:
The codebases are written in {language}.

## Examples of Existing Docstrings:
Here are some examples of docstrings that we have extracted from our codebases \
to give you a sense of the format and style of documentation we are aiming for:
{docstrings}

## Undocumented or Poorly Documented Code:
Here are is code that is either undocumented or poorly documented. Please \
generate docstrings for this code in the same style as the examples shown \
above:
{code}
"""

commit_prompt = """
I want you to act as a GitHub commit message generator.
Summarize the following explanations in 3-10 words. 
The summary should contain the most important information from each individual \
declaration.
Do not write any explanations or other words, just reply with the commit \
message.
The commit message should be a short, meaningful, and descriptive.
Avoid duplicate content in the commit message.

{tasks}
"""