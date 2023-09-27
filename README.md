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
You can verify the installation by checking the Poetry version with `poetry --version`

### Updating Poetry
Keep Poetry up to date by running `poetry self update`

### Uninstalling Poetry
If you ever need to uninstall Poetry, you can do so with the following commands:
```bash
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | POETRY_UNINSTALL=1 python3 -
```

## Managing Dependencies
### Adding a Dependency
To add a new Python dependency, simply use the following command: `poetry add dependencyName`

### Installing Dependencies
`poetry install` installs all project dependencies.

### Removing a Dependency
`poetry remove dependencyName` remove an installed dependency.

### Setting the Python Version
`poetry env use 3.10` specify the desired Python version for your project. For example, to set it to Python 3.10

## Running the Application
In the Makefile, you have the following targets:

`make run` Starts the Uvicorn server with the application. If it's not defined in the .env file, de default port is 8000.

`make delete-db` Deletes the application's database file if it exists. It will request confirmation before deletion.

`make test` Runs the application's tests using pytest and tracks code coverage.

`make coverage-report` Generates code coverage reports and opens them in a web browser (Firefox)

`make coverage-clean` Deletes previously generated coverage reports.

`make install` Installs project dependencies and creates the virtual environment using Poetry.

**Remember to create a .env file with the necessary environment variables before using the Makefile**
