lint_prompt = """
You will get two sections of code separated by ####. The first section \
contains source code that can be improved. A linter has already been used for \
this code to improve the code quality. The second code section contains the \
linter's suggestions for improving the code. Based on the linter's suggestions, \
return the improved source code. Try to improve the code quality independently \
and don't necessarily implement the linter suggestions 1:1.

Proceed as follows:
1. Analyze the source code and see if you recognize traditional coding \
conventions in the code.
2. Evaluate the linter suggestions
3. Apply changes that improve code quality and maintain the current coding \
convention if one is found.
4. Return a json object with 2 keys, "improved_source_code" and "explanation". \

####
source code:
{source_code}
####
linter suggestions:
{linter_suggestions}
####
"""