from typing import Dict, NamedTuple, Optional, Union

from .state_machine import StateMachine

class KvsGetRequest(NamedTuple):
    k: str

    def __str__(self) -> str:
        return f'get({self.k})'

    def __repr__(self) -> str:
        return str(self)

class KvsGetReply(NamedTuple):
    v: Optional[int]

    def __str__(self) -> str:
        return f'{self.v}'

    def __repr__(self) -> str:
        return str(self)

class KvsSetRequest(NamedTuple):
    k: str
    v: int

    def __str__(self) -> str:
        return f'set({self.k}, {self.v})'

    def __repr__(self) -> str:
        return str(self)

class KvsSetReply(NamedTuple):
    def __str__(self) -> str:
        return 'ok'

    def __repr__(self) -> str:
        return str(self)

class KvsAddRequest(NamedTuple):
    k: str
    x: int

    def __str__(self) -> str:
        return f'add({self.k}, {self.x})'

    def __repr__(self) -> str:
        return str(self)

class KvsAddReply(NamedTuple):
    success: bool

    def __str__(self) -> str:
        if self.success:
            return 'ok'
        else:
            return 'fail'

    def __repr__(self) -> str:
        return str(self)

State = Dict[str, int]
Input = Union[KvsGetRequest, KvsSetRequest]
Output = Union[KvsGetReply, KvsSetReply]
class Kvs(StateMachine[State, Input, Output]):
    def __init__(self):
        self.kvs: State = dict()

    def get(self, k: str) -> KvsGetRequest:
        return KvsGetRequest(k)

    def set(self, k: str, v: int) -> KvsSetRequest:
        return KvsSetRequest(k, v)

    def add(self, k: str, x: int) -> KvsAddRequest:
        return KvsAddRequest(k, x)

    # override.
    def reset(self) -> None:
        self.kvs = dict()

    # override.
    def transition(self, i: Input) -> Output:
        if isinstance(i, KvsGetRequest):
            return KvsGetReply(self.kvs.get(i.k, None))
        elif isinstance(i, KvsSetRequest):
            self.kvs[i.k] = i.v
            return KvsSetReply()
        elif isinstance(i, KvsAddRequest):
            if i.k in self.kvs:
                self.kvs[i.k] += i.x
                return KvsAddReply(True)
            else:
                return KvsAddReply(False)
        else:
            raise ValueError(f'Unrecognized input "{i}".')

    # override.
    def state(self) -> State:
        return self.kvs
