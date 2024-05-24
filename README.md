## Installation
Activate virtual environment and install requirements
```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Create file `.flaskenv` to set environment variables below
```
FLASK_DEBUG = True
FLASK_RUN_HOST="127.0.0.1"
FLASK_RUN_PORT=3000
```

Then run application with this command
```
flask --app src/main run
```
