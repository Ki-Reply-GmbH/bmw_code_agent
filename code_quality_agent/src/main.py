from code_quality_agent.src.file_retriever import FileRetriever
from code_quality_agent.src.docs_agent import DocsAgent

"""
python_files = FileRetriever("./tests").get_mapping()["py"]
print(python_files)
print()
"""

agent = DocsAgent(
    file_list = [
        "merge_agent/tests/unit/test_agent.py",
        "merge_agent/tests/unit/test_cache.py",
        "merge_agent/tests/unit/test_functions.py",
        "merge_agent/tests/unit/test_githandler.py",
    ],
    directory=".",
    language="python"
    )

print("Improving code...")
agent.make_docstrings()
