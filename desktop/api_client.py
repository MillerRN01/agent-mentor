import httpx


class AgentClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        try:
            response = httpx.get(f"{self.base_url}/api/health", timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}

    def chat(
        self,
        message: str,
        conversation_id: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """Envia mensagem e contexto para o backend."""
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "context": context,
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120.0,
            )

            if response.status_code >= 400:
                try:
                    detail = response.json()
                except Exception:
                    detail = {"detail": response.text}
                raise RuntimeError(detail.get("detail", str(detail)))

            return response.json()
        except httpx.ConnectError:
            raise RuntimeError(
                "Backend indisponível. Verifique se http://localhost:8000 está ativo."
            )
        except Exception as exc:
            raise RuntimeError(f"Erro de comunicação: {exc}")
