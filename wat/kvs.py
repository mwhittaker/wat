from typing import Dict, NamedTuple, Optional, Union

from .state_machine import StateMachine

class KvsGetRequest(NamedTuple):
    k: str

    def __str__(self) -> str:
        return f'get({self.k})'

class KvsGetReply(NamedTuple):
    v: Optional[str]

    def __str__(self) -> str:
        return f'{self.v}'

class KvsSetRequest(NamedTuple):
    k: str
    v: str

    def __str__(self) -> str:
        return f'set({self.k}, {self.v})'

class KvsSetReply(NamedTuple):
    def __str__(self) -> str:
        return ''

State = Dict[str, str]
Input = Union[KvsGetRequest, KvsSetRequest]
Output = Union[KvsGetReply, KvsSetReply]
class Kvs(StateMachine[State, Input, Output]):
    def __init__(self):
        self.kvs: State = dict()

    def get(self, k: str) -> KvsGetRequest:
        return KvsGetRequest(k)

    def set(self, k: str, v: str) -> KvsSetRequest:
        return KvsSetRequest(k, v)

    def reset(self) -> None:
        self.kvs = dict()

    def transition(self, i: Input) -> Output:
        if isinstance(i, KvsGetRequest):
            if i.k in self.kvs:
                return KvsGetReply(self.kvs[i.k])
            else:
                return KvsGetReply(None)
        elif isinstance(i, KvsSetRequest):
            self.kvs[i.k] = i.v
            return KvsSetReply()
        else:
            raise ValueError(f'Unrecognized input "{i}".')

    def state(self) -> State:
        return self.kvs
