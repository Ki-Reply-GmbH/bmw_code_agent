from file_retriever import FileRetriever
from docs_agent import DocsAgent

"""
python_files = FileRetriever("./tests").get_mapping()["py"]
print(python_files)
print()
"""

agent = DocsAgent(directory=".", language="python")

print("Improving code...")
agent.improve_code()

print("Writing changes...")
agent.write_changes()

print(agent)