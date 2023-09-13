# Makefile for running uvicorn with app and --reload

# Define the UVicorn command
UVICORN_CMD = uvicorn $(MAIN_FILE):$(APP_NAME) --reload

# Define the name of the main file and the app
MAIN_FILE = main
APP_NAME = app

# Define the 'run' target to run the UVicorn server within the virtual environment
run:
	$(UVICORN_CMD)
