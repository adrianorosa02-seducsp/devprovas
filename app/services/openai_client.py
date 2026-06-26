import os
from functools import lru_cache
from typing import Iterable, List, Sequence

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI
from openai.error import OpenAIError

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não está configurada.")
    return OpenAI(api_key=api_key)


def create_embeddings(texts: Sequence[str]) -> List[List[float]]:
    if not texts:
        return []
    client = get_openai_client()
    model = get_embedding_model()
    try:
        response = client.embeddings.create(model=model, input=list(texts))
    except OpenAIError as exc:
        raise RuntimeError("Falha ao gerar embeddings com o OpenAI.") from exc
    return [item.embedding for item in response.data]
