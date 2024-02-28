from file_retriever import FileRetriever
from lint_agent import LintAgent

"""
python_files = FileRetriever("./tests").get_mapping()["py"]
print(python_files)
print()
"""

agent = LintAgent(directory="./tests", language="java")
agent.improve_code()
agent.write_changes()
print(agent)