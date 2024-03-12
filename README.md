# Code Agent Documentation

## Table of Contents
- [Introduction](#introduction)
  - [Merge Agent](#merge-agent)
  - [Code Quality Agent](#code-quality-agent)
  - [Pull Request Agent](#pull-request-agent)
- [Technical Details](#technical-details)

## Introduction
The Code Agent is an AI-powered system designed to streamline various aspects of code management within a Git repository. This intelligent system springs into action when a pull request is opened or reopened, utilizing webhooks to trigger its operations. It comprises four main components:

#### Merge Agent
Designed to resolve merge conflicts in a Git repository. It analyzes which files have merge conflicts, solves them using an AI model and writes the resolved code back to the files.

#### Code Quality Agent
Analyzes code in terms of its quality and selects appropriate tools depending on the programming language. It improves the AI response by adding context to the prompt by using different linters.

#### Pull Request Agent
Responsible for updating the original pull request. The update describes the changes made by the previous agents.

#### Git Handler
The GitHandler class is the backbone of our git operations. It takes charge of initializing and cloning repositories, as well as creating an unique feature branch to which the agents' changes are committed and pushed.

## Technical Details

The Code Agent uses several Python libraries to perform its tasks:

| | |
|---|---|
| • Language: | <img src="https://img.shields.io/badge/python-v3.9-blue" alt="Python"> |
| • AI Model: | <img src="https://img.shields.io/badge/OpenAI-v1.13.3-brightgreen" alt="OpenAI"> |
| • Data Analysis: | <img src="https://img.shields.io/badge/Pandas-v2.2.1-yellow" alt="Pandas"> |
| • Testing: | <img src="https://img.shields.io/badge/Pytest-v6.2.5-red" alt="Pytest"> |
| • HTTP Requests: | <img src="https://img.shields.io/badge/Requests-v2.31.0-orange" alt="Requests"> |
| • Web Framework: | <img src="https://img.shields.io/badge/Flask-v3.0.2-green" alt="Flask"> |
| • WSGI Server: | <img src="https://img.shields.io/badge/Gunicorn-v21.2.0-blueviolet" alt="Gunicorn"> |
| • Code Analysis: | <img src="https://img.shields.io/badge/PMD-v6.38.0-blue" alt="PMD"> <img src="https://img.shields.io/badge/Black-v24.2.0-lightgrey" alt="Black">|

The Code Agent uses environment variables to configure the AI API key and the Git access token. It also uses a cache to store and retrieve data. The cache is used by the Merge Agent to store the AI's responses for resolving merge conflicts, which can be retrieved later to avoid making unnecessary API calls.

The Code Quality Agent uses different linters to check the code for potential issues. It also improves the AI's responses by adding context to the prompt. This helps the AI to generate more accurate and relevant responses.

The Pull Request Agent stores the changes made by the Merge Agent and the Code Quality Agent. It uses an AI to generate a summary of the changes for the pull request.
