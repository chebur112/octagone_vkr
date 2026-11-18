import json

import httpx
from openai import APIError, AsyncOpenAI

from app.config import settings


BASE_URL = "https://ai.api.cloud.yandex.net/v1"
MODEL_NAME = f"gpt://{settings.yc_folder_id}/yandexgpt-5.1"


class LLMError(Exception):
    """YandexGPT недоступна или вернула некорректный ответ."""


class YandexGPTClient:
    def __init__(self) -> None:
        self._http = httpx.AsyncClient(timeout=60)
        self._client = AsyncOpenAI(
            api_key=settings.yc_api_key,
            base_url=BASE_URL,
            http_client=self._http,
        )

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
    ) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
            )
        except (APIError, httpx.HTTPError) as error:
            raise LLMError("Не удалось обратиться к YandexGPT") from error

        content = response.choices[0].message.content

        if not content:
            raise LLMError("YandexGPT вернула пустой ответ")

        return content

    async def chat_json(
        self,
        messages: list[dict],
        schema: dict,
        temperature: float = 0.1,
    ) -> dict:
        try:
            response = await self._client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "result",
                        "strict": True,
                        "schema": schema,
                    },
                },
            )
        except (APIError, httpx.HTTPError) as error:
            raise LLMError("Не удалось получить JSON от YandexGPT") from error

        content = response.choices[0].message.content

        if not content:
            raise LLMError("YandexGPT вернула пустой ответ")

        try:
            result = json.loads(content)
        except json.JSONDecodeError as error:
            raise LLMError("YandexGPT вернула неправильный JSON") from error

        if not isinstance(result, dict):
            raise LLMError("YandexGPT вернула JSON не в виде объекта")

        return result

    async def close(self) -> None:
        await self._client.close()
