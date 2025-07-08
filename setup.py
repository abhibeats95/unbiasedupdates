from setuptools import setup, find_packages

setup(
    name="unbiasedupdates",  # Name of your package
    version="0.1.0",  # Version of your package
    packages=find_packages(),  # Automatically find packages
    install_requires=[],  # Add dependencies if needed
    include_package_data=True,  # Include non-code files like README.md
    description="News application extracting unbiased insights from the news articles using LLM",  # Short description
)
