# La Cosa (Backend) - Python Dependency Management and Execution Guide
Welcome to the La Cosa backend project! This guide will help you set up your development
environment and run the application using Poetry, a powerful Python dependency management
and packaging tool.

## Getting Started
### Installation
To get started, you'll need to install poetry. You can do this by running the following
command in your terminal:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Verify Installation
You can verify the installation by checking the poetry version with `poetry --version`

### Updating Poetry
Keep poetry up to date by running `poetry self update`

### Uninstalling Poetry
If you ever need to uninstall poetry, you can do so with the following commands:
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

`make run` starts the Uvicorn server with the application. If it's not defined in the .env file, de default port is 8000.

`make create-seed-data` Populates the database with 6 players and 1 game.

`make delete-db` deletes the application's database file if it exists. It will request confirmation before deletion.

`make test-all` runs the application's tests using pytest and tracks code coverage.

`make coverage-report` generates code coverage reports and opens them in a web browser (Firefox)

`make coverage-clean` deletes previously generated coverage reports.

`make autopep8` formats all the Python files to the PEP8 standard.

`make install` installs project dependencies and creates the virtual environment using poetry.

**Remember to create a .env file with the necessary environment variables before using the Makefile**
**To know the necessary environment variables you can see the `.env.example` file.**


## Running the Application in Containers - Docker

### Building the Docker Image
`docker build -t backend-tuki .`

### Run a container based on the built image
`docker run --name backend-tuki-container -p 8000:8000 backend-tuki`

## Running the Application in Containers - Docker Compose
`docker-compose up --build`
