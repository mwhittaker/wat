from typing import Dict, List, NamedTuple, Optional, Union

from .state_machine import StateMachine

class ListsLpushRequest(NamedTuple):
    x: str

class ListsLpushReply(NamedTuple):
    success: bool

class ListsLpopRequest(NamedTuple):
    pass

class ListsLpopReply(NamedTuple):
    x: Optional[str]

class ListsRpushRequest(NamedTuple):
    x: str

class ListsRpushReply(NamedTuple):
    success: bool

class ListsRpopRequest(NamedTuple):
    pass

class ListsRpopReply(NamedTuple):
    x: Optional[str]

class ListsRemoveRequest(NamedTuple):
    x: str

class ListsRemoveReply(NamedTuple):
    success: bool

class ListsSetRequest(NamedTuple):
    x: str
    i: int

class ListsSetReply(NamedTuple):
    success: bool

class ListsIndexRequest(NamedTuple):
    i: int

class ListsIndexReply(NamedTuple):
    x: Optional[str]


Input = Union[ListsLpushRequest, ListsLpopRequest, ListsRpushRequest,
              ListsRpopRequest, ListsRemoveRequest, ListsSetRequest,
              ListsIndexRequest]
Output = Union[ListsLpushReply, ListsLpopReply, ListsRpushReply,
               ListsRpopReply, ListsRemoveReply, ListsSetReply, ListsSetReply,
               ListsIndexReply]
class Lists(StateMachine[Input, Output]):
    def __init__(self):
        self.xs: List[str] = []

    def lpush(self, x: str) -> ListsLpushRequest:
        return ListsLpushRequest(x)

    def lpop(self) -> ListsLpopRequest:
        return ListsLpopRequest()

    def rpush(self, x: str) -> ListsRpushRequest:
        return ListsRpushRequest(x)

    def rpop(self) -> ListsRpopRequest:
        return ListsRpopRequest()

    def remove(self, x: str) -> ListsRemoveRequest:
        return ListsRemoveRequest(x)

    def set(self, x: str, i: int) -> ListsSetRequest:
        return ListsSetRequest(x, i)

    def index(self, i: int) -> ListsIndexRequest:
        return ListsIndexRequest(i)

    # override.
    def reset(self) -> None:
        self.xs = []

    # override.
    def transition(self, i: Input) -> Output:
        if isinstance(i, ListsLpushRequest):
            self.xs = [i.x] + self.xs
            return ListsLpushReply(True)
        elif isinstance(i, ListsLpopRequest):
            if len(self.xs) == 0:
                return ListsLpopReply(None)
            else:
                return ListsLpopReply(self.xs.pop(0))
        elif isinstance(i, ListsRpushRequest):
            self.xs.append(i.x)
            return ListsRpushReply(True)
        elif isinstance(i, ListsRpopRequest):
            if len(self.xs) == 0:
                return ListsRpopReply(None)
            else:
                return ListsRpopReply(self.xs.pop(len(self.xs) - 1))
        elif isinstance(i, ListsRemoveRequest):
            if i.x in self.xs:
                self.xs.remove(i.x)
            return ListsRemoveReply(True)
        elif isinstance(i, ListsSetRequest):
            if 0 <= i.i < len(self.xs):
                del self.xs[i.i]
                return ListsSetReply(True)
            else:
                return ListsSetReply(False)
        elif isinstance(i, ListsIndexRequest):
            if 0 <= i.i < len(self.xs):
                return ListsIndexReply(self.xs[i.i])
            else:
                return ListsIndexReply(None)
        else:
            raise ValueError(f'Unrecognized input "{i}".')
