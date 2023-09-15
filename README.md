# La Cosa (Backend) - Python Dependency Management and Execution Guide
Welcome to the La Cosa backend project! This guide will help you set up your development
environment and run the application using Poetry, a powerful Python dependency management
and packaging tool.

## Getting Started
### Installation
To get started, you'll need to install Poetry. You can do this by running the following
command in your terminal:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Verify Installation
You can verify the installation by checking the Poetry version:
```bash
poetry --version
```

### Updating Poetry
Keep Poetry up to date by running:
```bash
poetry self update
```

### Uninstalling Poetry
If you ever need to uninstall Poetry, you can do so with the following commands:
```bash
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | POETRY_UNINSTALL=1 python3 -
```

## Managing Dependencies
### Adding a Dependency
To add a new Python dependency, simply use the following command:
```bash
poetry add dependencyName
```

### Installing Dependencies
Install all project dependencies by running:
```bash
poetry install
```

### Removing a Dependency
If you need to remove an installed dependency, you can do so with:
```bash
poetry remove dependencyName
```

### Setting the Python Version
You can specify the desired Python version for your project. For example, to set it to Python 3.10:
```bash
poetry env use 3.10
```

## Running the Application
To execute the application, follow these steps:
1. Install project dependencies:
```bash
poetry install
```
2. Activate the virtual environment:
```bash
poetry shell
```
3. Run the application:
```bash
make run
```
