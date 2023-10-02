# Makefile for running uvicorn with app and --reload
-include .env

# Define a default value for PORT in case it's not defined in .env
ifndef PORT
PORT = 8000
endif

# Define the name of the main file and the app
MAIN_FILE = app.main
APP_NAME = app

# Define the path to the database file
DB_FILE = ./app/database/*.sqlite

# Define the path to the test database file
TEST_DB_FILE = ./app/database/database_test.sqlite

# Define the UVicorn command
UVICORN_CMD = uvicorn $(MAIN_FILE):$(APP_NAME) --port $(PORT) --reload

.PHONY: run delete-db test coverage-report coverage-clean

# Define the 'run' target to run the UVicorn server within the virtual environment
run: install
	poetry run $(UVICORN_CMD)

# Define the 'delete-db' target to delete the database file
delete-db:
	@if [ -f $(DB_FILE) ]; then \
		read -p "Are you sure you want to delete the database? [y/N]: " confirm; \
		if [ "$$confirm" = "y" ]; then \
			rm -f $(DB_FILE); \
			echo "Database deleted."; \
		else \
			echo "Database not deleted."; \
		fi; \
	else \
		echo "Database file not found. No action taken."; \
	fi

# Define the path to the tests directory
TEST_DIRECTORY = ./app/tests

# Define the 'test-games' target to run game tests in the test environment
test-games: install
	ENVIRONMENT=test poetry run coverage run -m pytest -vv $(TEST_DIRECTORY)/game_tests; true
	rm -f $(TEST_DB_FILE)
	unset ENVIRONMENT

# Define the 'test-players' target to run player tests in the test environment
test-players: install
	ENVIRONMENT=test poetry run coverage run -m pytest -vv $(TEST_DIRECTORY)/player_tests; true
	rm -f $(TEST_DB_FILE)
	unset ENVIRONMENT


# Define the 'test-all' target to run all tests sequentially
test-all: test-games test-players

# Define the 'coverage-report' target to generate coverage reports
coverage-report:
	poetry run coverage html
	@firefox htmlcov/index.html

# Define the 'coverage-clean' target to remove coverage reports
coverage-clean:
	@rm -rf htmlcov
	@echo "Coverage report deleted."

# Define the 'autopep8' target for running autopep8
autopep8:
	poetry run autopep8 --in-place --recursive .

# Define the 'install' target to install dependencies and create the virtual environment
install: pyproject.toml
	poetry install

# .env file dependency
.env:
	@echo "Please create a .env file with the necessary environment variables (see in .env.example file)." && exit 1
