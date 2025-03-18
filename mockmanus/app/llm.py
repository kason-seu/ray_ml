from typing import Dict, Optional, Any, List, Union

from openai import AsyncAzureOpenAI, AsyncOpenAI, OpenAIError

from mockmanus.app.config import LLMSettings
from mockmanus.app.config import config
from mockmanus.app.logger import logger
from mockmanus.app.schema import Message

from tenacity import retry, wait_random_exponential, stop_after_attempt


class LLM:
    _instances: Dict[str, "LLM"] = {}

    def __new__(cls,
                config_name: str = "default",
                llm_config: Optional[LLMSettings] = None,
                *args, **kwargs):
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance

        return cls._instances[config_name]

    def __init__(self, /, config_name: str = "default", llm_config: Optional[LLMSettings] = None):
        if not hasattr(self, "client"):  # Only initialized if not already initialized
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config["default"])
            # create llm client
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.api_type = llm_config.api_type
            self.api_key = llm_config.api_key
            self.api_version = llm_config.api_version
            self.base_url = llm_config.base_url
            if self.api_type == "azure":
                self.client = AsyncAzureOpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    api_version=self.api_version,
                )
            else:
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    @staticmethod
    def format_messages(messages: List[Union[dict, Message]]) -> List[dict]:
        """
                Format messages for LLM by converting them to OpenAI message format.

                Args:
                    messages: List of messages that can be either dict or Message objects

                Returns:
                    List[dict]: List of formatted messages in OpenAI format

                Raises:
                    ValueError: If messages are invalid or missing required fields
                    TypeError: If unsupported message types are provided

                Examples:
                    >>> msgs = [
                    ...     Message.system_message("You are a helpful assistant"),
                    ...     {"role": "user", "content": "Hello"},
                    ...     Message.user_message("How are you?")
                    ... ]
                    >>> formatted = LLM.format_messages(msgs)
        """
        formatted_messages = []
        for message in messages:
            if isinstance(message, dict):
                # if message is already a dict, ensure it has requires fields
                if 'role' not in message:
                    raise ValueError("Message dict must contain 'role' field")
                formatted_messages.append(message)
            elif isinstance(message, Message):
                # If message is a Message object, convert it to a dict
                formatted_messages.append(message.to_dict())
            else:
                raise TypeError(f"Unsupported message type: {type(message)}")

        # Validate all messages have required fields
        for msg in formatted_messages:
            if msg["role"] not in ["system", "user", "assistant", "tool"]:
                raise ValueError(f"Invalid role: {msg['role']}")
            if "content" not in msg and "tool_calls" not in msg:
                raise ValueError(
                    "Message must contain either 'content' or 'tool_calls'"
                )

        return formatted_messages

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6)
    )
    async def ask(
            self,
            messages: List[Union[dict, Message]],
            system_msgs: Optional[List[Union[dict, Message]]] = None,
            stream: bool = True,
            temperature: Optional[float] = None
    ) -> str:
        """
        Send a prompt to the llm and get the response
        :param messages: List of conversation messages
        :param system_msgs: Optional system messages to prepend
        :param stream:Whether to stream the response
        :param temperature: Sampling temperature for the response
        :return: The generated response

        Raises:
            ValueError: If messages are invalid or response is empty
            OpenAIError: If API call fails after retries
            Exception: For unexpected errors
        """
        try:
            # Format optional system and user messages
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)

            if not stream:  # 同步获取reponse
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=temperature or self.temperature,
                    stream=False
                )
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError('Empty or valid response from llm')

                return response.choices[0].message.content

            # Streaming Response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                stream=True,
            )

            collected_messages = []
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
                print(chunk_message, end="", flush=True)

            print()  # NEWLINE after streaming
            full_response = "".join(collected_messages).strip()
            if not full_response:
                raise ValueError("Empty response from streaming llm")
            return full_response

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"OpenAi Api error: {oe}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in ask: {e}")
            raise
