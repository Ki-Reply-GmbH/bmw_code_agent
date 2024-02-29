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