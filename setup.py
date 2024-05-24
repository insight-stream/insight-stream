from setuptools import setup, find_packages

setup(
    name="insight_stream",
    version="1.0.0",
    description="InsightStream python library and scripts",
    packages=find_packages(),
    install_requires=[
        "openai",
        "langchain",
        "langchain-core",
        "langchain-openai",
        "langchain-community",
        "langchain_text_splitters",
        "numpy",
        "unstructured",
        "unstructured[docx]",
        "unstructured[pdf]",
        "python-dotenv",
        "qdrant_client",
    ],
    python_requires=">=3.10",
)
