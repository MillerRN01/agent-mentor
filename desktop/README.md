# Agent Mentor

Assistente de desktop e backend para suporte contextual em programação.

## Estrutura

- backend/
- desktop/

## Backend

Roda em FastAPI + Ollama + SQLite.

### Iniciar backend
```powershell
cd D:\agent-mentor\backend
..\ .venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
