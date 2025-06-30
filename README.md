# INC-URL-Analyzer
INC project to analyze social URLs

---

## 🛠️ Project Setup & Execution

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run the Project (Locally)

#### 2.1 Using uv command
```bash
ENV=local uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2.2 Using sh script
```bash
sh run-local.sh
```

### 3. Run with Docker

```bash
docker build -t softphone-app .
docker run -p 8000:8000 softphone-app
```

### 4. Run for prod or stage environment

- For prod
```bash
sh run-prod.sh
```

- For Stage
```bash
sh run-stage.sh
```

---

## Enivorment variable

All the variable configs are done ```core/configs.py``` file.

 - For local (.env.local)
 - For Stage (.env.stage)
 - For Prod (.env.prod)


## Folder Structure
```code
 |- api/
    |- v1/
        |- api.py         # Common file for route configuration
        |- routes/
            |- file.py    # File for routing
 |- core/
    |- configs.py         # Contains env configs and variables
    |- seed_db.py         # Contains logic for db faking
    |- session.py         # DB connection logic
 |- models/
    |- enums/
        |- file.py        # Files for enums
    |- file.py            # Files for db models
 |- schemas/
    |- responses/
        |- file.py        # File for responses schemas
 |- services/
    |- file.py            # File for services
 |- utils/
    |- file.py            # Utility files
 |- main.py               # main file
```

## 📦 GitHub Commit Rules

Please follow the below tagging convention in commit messages:

| Tag     | Description                                                   |
|---------|---------------------------------------------------------------|
| `ADDED`   | For adding new files, directories, or features               |
| `UPDATED` | For updating existing files, directories, or features        |
| `FIXES`   | For fixing bugs                                               |
| `CHANGES` | For architectural or structural changes                      |

**Example Commit Message:**
```
ADDED: Implemented initial Twilio call webhook integration
```
