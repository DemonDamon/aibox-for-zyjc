# Date    : 2024/6/26 19:05
# File    : qwen_langchain_service.py
# Desc    :
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import time
import json
import uuid
from typing import Any, Iterator, List, Optional

import requests
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain_core.outputs import GenerationChunk

from utils.logger_utils import logger
from utils.sse_client import SSEClient


class Qwen(LLM):
    """Qwen LLM API service.

    Example:
        .. code-block:: python

            from qwen_langchain_service import Qwen
            qwen = Qwen(endpoint_url="http://192.168.32.113:7820/aibox/v1/llm/chat/completions")
    """

    endpoint_url: str = "http://192.168.32.113:7820/aibox/v1/llm/chat/completions"
    """Base URL of the Qwen API service."""
    max_tokens: int = 8000
    """Max token allowed to pass to the model."""
    temperature: float = 0.1
    """LLM model temperature from 0 to 10."""
    messages: List[dict] = []
    """History of the conversation"""
    top_p: float = 0.7
    """Top P for nucleus sampling from 0 to 1"""
    stream_flag: bool = False
    """Whether to use streaming chat or not"""
    model: str = "Qwen1.5-32B-Chat-GPTQ-Int4"
    """Qwen model to use"""

    @property
    def _llm_type(self) -> str:
        return "qwen"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """Call out to a Qwen LLM inference endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = Qwen_llm("Who are you?")
        """

        # HTTP headers for authorization
        headers = {"Content-Type": "application/json"}

        self.messages = [{"role": "user", "content": prompt}]

        payload = json.dumps({
            "request_id": str(uuid.uuid4().hex),
            "model": self.model,
            "messages": self.messages,
            "stream": self.stream_flag,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p
        })

        logger.debug(f"Qwen payload: {payload}")

        # call api
        try:
            response = requests.request("POST", self.endpoint_url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        logger.debug(f"Qwen response: {response}")

        if response.status_code != 200:
            raise ValueError(f"Failed with response: {response}")

        try:
            parsed_response = response.json()

            # Check if response content does exists
            if isinstance(parsed_response, dict):
                content_keys = "data"
                if content_keys in parsed_response:
                    text = parsed_response['data']['choices'][0]['message']['content']
                else:
                    raise ValueError(f"No content in response : {parsed_response}")
            else:
                raise ValueError(f"Unexpected response type: {parsed_response}")

        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(
                f"Error raised during decoding response from inference endpoint: {e}."
                f"\nResponse: {response.text}"
            )

        return text

    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        headers = {"Content-Type": "application/json"}

        self.messages = [{"role": "user", "content": prompt}]

        payload = json.dumps({
            "request_id": str(uuid.uuid4().hex),
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p
        })

        logger.debug(f"Qwen payload: {payload}")
        # call api
        try:
            response = requests.request("POST", self.endpoint_url, headers=headers, data=payload)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        if response.status_code != 200:
            raise ValueError(f"Failed with response: {response}")

        sse_client = SSEClient(response)
        for event in sse_client.events(is_async=False):
            parsed_response = json.loads(event.data)
            delta = parsed_response["choices"][0]["delta"]
            text = delta.get("content", None)
            if text is None:
                continue

            request_id = parsed_response["id"]
            finish_reason = parsed_response["choices"][0]["finish_reason"]
            chunk = GenerationChunk(
                text=text,
                generation_info=dict(
                    finish_reason=finish_reason,
                    request_id=request_id,
                )
            )

            if "usage" in parsed_response.keys():
                token_usage = parsed_response["usage"]["total_tokens"]
                chunk.generation_info["token_usage"] = token_usage

            if run_manager:
                run_manager.on_llm_new_token(chunk.text)
            yield chunk

            if finish_reason is not None:
                break
