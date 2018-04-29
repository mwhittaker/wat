from typing import Dict, List, NamedTuple, Optional, Union

from .state_machine import StateMachine

class Expr:
    def eval(self, env: Dict[str, bool]) -> bool:
        raise NotImplementedError()

class Top(Expr):
    def __str__(self) -> str:
        return 'true'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return True

class Bot(Expr):
    def __str__(self) -> str:
        return 'false'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return False

class Var(Expr):
    def __init__(self, x: str) -> None:
        self.x = x

    def __str__(self) -> str:
        return 'false'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return env.get(self.x, False)

class And(Expr):
    def __init__(self, children: List[Expr]) -> None:
        self.children = children

    def __str__(self) -> str:
        return f'And{self.children}'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return all(child.eval(env) for child in self.children)

class Or(Expr):
    def __init__(self, children: List[Expr]) -> None:
        self.children = children

    def __str__(self) -> str:
        return f'Or{self.children}'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return any(child.eval(env) for child in self.children)

class Not(Expr):
    def __init__(self, child: Expr) -> None:
        self.child = child

    def __str__(self) -> str:
        return f'Not[{self.child}]'

    def __repr__(self) -> str:
        return str(self)

    def eval(self, env: Dict[str, bool]) -> bool:
        return not self.child.eval(env)

class BexprEvalRequest(NamedTuple):
    e: Expr

    def __str__(self) -> str:
        return f'eval({self.e})'

    def __repr__(self) -> str:
        return str(self)

class BexprEvalReply(NamedTuple):
    b: bool

    def __str__(self) -> str:
        return f'{self.b}'

    def __repr__(self) -> str:
        return str(self)

class BexprSetRequest(NamedTuple):
    k: str

    def __str__(self) -> str:
        return f'set({self.k})'

    def __repr__(self) -> str:
        return str(self)

class BexprSetReply(NamedTuple):
    def __str__(self) -> str:
        return 'ok'

    def __repr__(self) -> str:
        return str(self)

class BexprUnsetRequest(NamedTuple):
    k: str

    def __str__(self) -> str:
        return f'unset({self.k})'

    def __repr__(self) -> str:
        return str(self)

class BexprUnsetReply(NamedTuple):
    def __str__(self) -> str:
        return 'ok'

    def __repr__(self) -> str:
        return str(self)

Input = Union[BexprEvalRequest, BexprSetRequest, BexprUnsetRequest]
Output = Union[BexprEvalReply, BexprSetReply, BexprUnsetReply]
class Bexpr(StateMachine[Input, Output]):
    def __init__(self):
        self.env: Dict[str, bool] = dict()

    def eval(self, e: Expr) -> BexprEvalRequest:
        return BexprEvalRequest(e)

    def set(self, k: str) -> BexprSetRequest:
        return BexprSetRequest(k)

    def unset(self, k: str) -> BexprUnsetRequest:
        return BexprUnsetRequest(k)

    # override.
    def reset(self) -> None:
        self.env = dict()

    # override.
    def transition(self, i: Input) -> Output:
        if isinstance(i, BexprEvalRequest):
            return BexprEvalReply(i.e.eval(self.env))
        elif isinstance(i, BexprSetRequest):
            self.env[i.k] = True
            return BexprSetReply()
        elif isinstance(i, BexprUnsetRequest):
            self.env[i.k] = False
            return BexprUnsetReply()
        else:
            raise ValueError(f'Unrecognized input "{i}".')
