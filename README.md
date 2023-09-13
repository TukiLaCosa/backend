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

### Run environment
```console
poetry shell
```
