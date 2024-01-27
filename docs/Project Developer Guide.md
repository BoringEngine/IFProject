# IFProject Developer Guide

Welcome to the Developer Guide for IFProject. This guide is intended for those who wish to contribute to the development of IFProject, a Python-based interactive fiction engine. Here, you'll find detailed information on the tools and processes we use for development.

## Getting Started
Before diving into development, ensure you have completed the initial setup steps outlined in the IFProject [README](../README.md). This includes forking and cloning the repository, setting up your virtual environment, and installing the project in editable mode.


# Code Contributions
When contributing code, please adhere to the following process:

1. **Pull the Latest Changes**: Always pull the latest changes from the main branch before starting your work.

2. **Create a Feature Branch**: Work on a separate branch for each feature or bug fix.

3. **Stack Commits**: Squash your commits into a stack of independent, well tested topic commits.

4. **Write Docs**: Ensure additions and modifications have clean doc strings. Update guides if necessary.
5. 
6. **Write Tests**: If you add new features or fix bugs, write corresponding tests.

7. **Run Tests**: Before submitting a pull request, run all tests to ensure your changes don't break anything.

8. **Follow Coding Standards**: Run Flake8 to ensure your code follows our coding standards.

9. **Submit a Pull Request**: Once your changes are complete, submit a pull request for review.

**Contributing Guidelines**: Please read our contributing guidelines before submitting your pull requests. [Link](Contributor Guidelines.md)

## Further Reading
- **User Guide**: For details on how to use IFProject as a user, refer to our dedicated user guide. [[Link]](User Guide.md)
- **Contributing Guidelines**: Please read our contributing guidelines before submitting your pull requests. [Link](Contributor Guidelines.md)


# Project Tools
IFProject utilizes several tools to maintain code quality, facilitate testing, and manage releases. Here's an overview of each tool and how to use them:

### 1. Pytest
- **Purpose**: Pytest is used for running automated tests to ensure code changes do not break existing functionality.
- **Usage**:
  ```
  pytest
  ```
  Run this command in the root directory of the project to execute all tests.

### 2. Ruff
- **Purpose**: Ruff is a tool for enforcing coding standards and checking for syntax errors.
- **Usage**:
  ```
  ruff check   # Check and fix linting issues
  ruff format  # Format project
  ```

### 3. Clean
- **Purpose**: The 'clean' command is used to remove caches and build artifacts, ensuring a clean state for builds or tests.
- **Usage**:
  ```
  clean
  ```
  This will clear out the `__pycache__` directories and the `build/` or `dist/` directories. Use this if tests are throwing suspicious failures.

### 4. Twine
- **Purpose**: Twine is a utility for publishing Python packages on package repositories like PyPI.
- **Usage**:
  ```
  twine upload dist/*
  ```
  Ensure you have built the package before running this command.

## Recommended extensions

If you're using VSCode, these are the extensions we've found helpful. You can install them by copying the commands into your shell.

Please review the items carefully and pick the items you need.

Note: Copilot requires a subscription. We'll be recommending an open source tool soon.



```shell

# Python Development Tools
code --install-extension ms-python.python                          # Essential Python support (intellisense, debugging, etc.)
code --install-extension ms-python.vscode-pylance                  # Advanced Python language support with Pylance
code --install-extension charliermarsh.ruff                        # Automatically Format and Lint Python using Ruff
code --install-extension donjayamanne.python-environment-manager   # Manages and switches between Python environments

# Testing
code --install-extension littlefoxteam.vscode-python-test-adapter  # Adapter for running Python tests in VS Code
code --install-extension ms-vscode.test-adapter-converter          # Convert different testing frameworks to a standard format
code --install-extension hbenl.vscode-test-explorer                # Explorer for running and managing tests

# Yaml Development Tools
code --install-extension redhat.vscode-yaml                        # YAML language support, with schemas and validation

# Web Development Tools
code --install-extension ritwickdey.LiveServer                     # Local development server with live reload feature

# Collaborative coding
code --install-extension ms-vsliveshare.vsliveshare                # Team coding with audio in a shared Vscode environemnt

# Markdown and Documentation Tools
code --install-extension yzhang.markdown-all-in-one                # Markdown formatting and table of contents
code --install-extension bierner.markdown-mermaid                  # Mermaid diagram support
code --install-extension yzane.markdown-pdf                        # Convert Markdown files to PDF (useful for proofreading)

# GitHub Integration and Tools
code --install-extension github.vscode-github-actions              # Integration for GitHub Actions
code --install-extension GitHub.vscode-pull-request-github         # Pull request and issue management for GitHub

# AI Tools
code --install-extension GitHub.copilot                            # AI assisted autcomplete and commit messages
```


## Need Help?
If you encounter any issues or need further assistance, feel free to join the [IFProject Discord](https://discord.gg/2DU6pwVn).
