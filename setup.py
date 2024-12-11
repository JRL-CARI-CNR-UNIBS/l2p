from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="lang2pddl",
    version="0.1.4",
    packages=find_packages(exclude=["tests"]),
    description="Library to connect LLMs and planning tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marcus Tantakoun",
    author_email="mtantakoun@gmail.com",
    install_requires=[
        "openai",
        "tiktoken",
        "retry",
        "pddl",
        "typing_extensions",
        "transformers>=4.43.1",
        "torch>=2.2",
        "accelerate>=0.26.0",
    ],
    license="MIT",
    url="https://github.com/AI-Planning/l2p",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
