# Makefile for running uvicorn with app and --reload
include .env

# Define a default value for PORT in case it's not defined in .env
ifndef PORT
PORT = 8000
endif

# Define the UVicorn command
UVICORN_CMD = uvicorn $(MAIN_FILE):$(APP_NAME) --port $(PORT) --reload

# Define the name of the main file and the app
MAIN_FILE = app.main
APP_NAME = app

# Define the 'run' target to run the UVicorn server within the virtual environment
run:
	$(UVICORN_CMD)
