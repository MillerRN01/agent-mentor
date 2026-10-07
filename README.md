# Agent Mentor

Backend local do Agent Mentor com FastAPI, Ollama e SQLite.

## Estrutura proposta

- `backend/`: API principal em FastAPI
- `desktop/`: aplicativo desktop para interagir com o backend

## Execução do backend

```powershell
cd D:\agent-mentor\backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa:

```text
http://localhost:8000/docs
```
