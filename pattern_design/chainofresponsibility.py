import abc
from abc import ABC


class Handle(abc.ABC):

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def handle(self, request) -> bool:
        pass


class DefaultHandle(Handle):
    def __init__(self):
        super().__init__()

    def handle(self, request) -> bool:
        print(f'the end of the chain, use defaulthandle to handle the request')
        return True


class FirstHandle(Handle):

    def __init__(self, handle: Handle = DefaultHandle()):
        super().__init__()
        self.next_handle = handle

    def handle(self, request) -> bool:
        if 0 < request < 10:
            print(f'FirstHandle handle the request {request} and finish the task')
            print("============END=========\n")
            return True
        print(f'FirstHandle cannot handle the request {request} and dispatch to the next handle')
        return self.next_handle.handle(request)


class SecondHandle(Handle):

    def __init__(self, handle: Handle = DefaultHandle()):
        super().__init__()
        self.next_handle = handle

    def handle(self, request) -> bool:
        if 10 < request < 20:
            print(f'SecondHandle handle the request {request} and finish the task~~~')
            print("============END=========\n")
            return True
        print(f'SecondHandle cannot handle the request {request} and dispatch to the next handle')
        return self.next_handle.handle(request)


class Client:

    def __init__(self, handle: Handle):
        self._handle = handle

    def handle(self, *requests):
        for request in requests:
            self._handle.handle(request)


second = SecondHandle()
first = FirstHandle(second)

c = Client(first)
c.handle(5, 15, 50)
