# La Cosa (backend)

## Poetry (Python dependency management and packaging tool)
### Installation
```console
curl -sSL https://install.python-poetry.org | python3 -
```

### To see version
```console
poetry --version
```

### To update
```console
poetry self update
```

### To uninstall
```console
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | POETRY_UNINSTALL=1 python3 -
```

### Specifying dependencies
```console
poetry add dependencyName
```

### Installing dependencies
```console
poetry install
```

### Removing an installed package
```console
poetry remove packageName
```

### To set the desired Python version (example 3.10)
```console
poetry env use 3.10
```

### Run environment
```console
poetry shell
```

## To execute the application
```console
poetry install
poetry shell
make run
```
