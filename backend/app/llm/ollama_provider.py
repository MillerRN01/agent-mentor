import httpx

from app.core.config import settings


class OllamaProviderError(Exception):
    """Raised when Ollama cannot generate a response."""


class OllamaProvider:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise OllamaProviderError("Ollama demorou demais para responder.") from exc
        except httpx.ConnectError as exc:
            raise OllamaProviderError(
                "Não foi possível conectar ao Ollama. Verifique se ele está rodando."
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaProviderError(
                "Ollama retornou uma resposta inválida ou um erro HTTP."
            ) from exc

        answer = data.get("response")
        if not isinstance(answer, str) or not answer.strip():
            raise OllamaProviderError("Ollama não retornou texto na resposta.")
        return answer.strip()
