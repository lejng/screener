# Commands (os windows)

### 1. Determinate is it virt env or not
```
where pip
```

### 2. Activate virtual env or create virtual env
activate
```
.venv\Scripts\activate
```
create:
```
python -m venv .venv
```

### 3. Install/remove dependencies
```
pip install -r requirements.txt

pip uninstall -r requirements.txt
```

### 4. How to run
```
python -m src.main_ui

python -m src.main_console
```

### 5. Deactivate virtual env
```
deactivate
```