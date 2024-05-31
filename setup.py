from setuptools import setup, find_packages

setup(
    name="insightStream",
    version="1.0.0",
    description="InsightStream python library and scripts",
    license='MIT',
    packages=['insightStream'],
    install_requires=[
        "openai",
        "langchain",
        "langchain-core",
        "langchain-openai",
        "langchain-community",
        "langchain_qdrant",
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
