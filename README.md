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

### 4. Deactivate virtual env
```
deactivate
```

### 5. How to run console app
```
python -m src.main_console
```

### 6. How to run web app (dev mode)
```
uvicorn src.main_web:app --port 8000 --reload
uvicorn src.main_web:app --port 8000
```

### 7. Endpoints
```
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## Docker Commands

### 8. Run with Docker Compose
```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Start without rebuild
docker-compose up
```

### 9. Stop Docker containers
```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### 10. Docker endpoints
```
http://localhost:8000/
http://localhost:8000/docs
```