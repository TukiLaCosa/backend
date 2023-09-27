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
In the Makefile, you have the following targets:

```bash
make run
```
Starts the Uvicorn server with the application. If it's not defined in the .env file, de default port is 8000.

```bash
make delete-db
```

Deletes the application's database file if it exists. It will request confirmation before deletion.

```bash
make test
```
Runs the application's tests using pytest and tracks code coverage.

```bash
make coverage-report
```
Generates code coverage reports and opens them in a web browser (Firefox)

```bash
make coverage-clean
```
Deletes previously generated coverage reports.

```bash
make install
```
Installs project dependencies and creates the virtual environment using Poetry.

**Remember to create a .env file with the necessary environment variables before using the Makefile**
