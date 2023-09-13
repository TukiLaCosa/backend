# Makefile for running uvicorn with app and --reload

# Set the default target to 'init'
# .DEFAULT_GOAL := init

# Define the Poetry command
POETRY_CMD = poetry

# Define the UVicorn command
UVICORN_CMD = uvicorn $(MAIN_FILE):$(APP_NAME) --reload

# Define the name of the main file and the app
MAIN_FILE = main
APP_NAME = app

# Define the 'init' target to create a virtual environment and run the server
init:
	$(POETRY_CMD) install
	$(POETRY_CMD) shell

# Define the 'run' target to run the UVicorn server
run:
	$(POETRY_CMD) run $(UVICORN_CMD)
