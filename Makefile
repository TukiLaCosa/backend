# Makefile for running uvicorn with app and --reload
-include .env

# Define a default value for PORT in case it's not defined in .env
ifndef PORT
PORT = 8000
endif

# Define the UVicorn command
UVICORN_CMD = uvicorn $(MAIN_FILE):$(APP_NAME) --port $(PORT) --reload

# Define the name of the main file and the app
MAIN_FILE = app.main
APP_NAME = app

# Define the path to the database file
DB_FILE = ./app/database/*.sqlite

# Define the 'run' target to run the UVicorn server within the virtual environment
run:
	$(UVICORN_CMD)

# Define the 'delete-db' target to delete the database file
delete-db:
	@if [ -f $(DB_FILE) ]; then \
		read -p "Are you sure you want to delete the database? [y/N]: " confirm; \
		if [ "$$confirm" == "y" ]; then \
			rm -f $(DB_FILE); \
			echo "Database deleted."; \
		else \
			echo "Database not deleted."; \
		fi; \
	else \
		echo "Database file not found. No action taken."; \
	fi
