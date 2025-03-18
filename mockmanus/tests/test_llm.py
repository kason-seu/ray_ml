import asyncio

from mockmanus.app.llm import LLM
from mockmanus.app.schema import Message


def build() -> LLM:
    llm = LLM()
    return llm


async def main():
    llm = build()
    msgs = [
        Message.system_message("You are a helpful assistant"),
        {"role": "user", "content": "Hello"},
        Message.user_message("How are you?")
    ]
    result = await llm.ask(messages=msgs, stream=False)
    return result


async def llm():
    re = await main()
    print(re)
    llm = build()
    msg = "what is the result of 1 + 1"
    add = await llm.ask(messages=[Message.user_message(msg)], stream=False)
    print(f'add = {add}')


asyncio.run(llm())
