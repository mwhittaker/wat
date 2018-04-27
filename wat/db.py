from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Union

from .state_machine import StateMachine

class QueryException(Exception):
    pass

class Query:
    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        raise NotImplementedError()

class Relation(Query):
    def __init__(self, r: str) -> None:
        self.r = r

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        if self.r not in db:
            raise QueryException(f'{self.r} not in {db}.')
        return db[self.r]

    def __str__(self) -> str:
        return f'{self.r}'

    def __repr__(self) -> str:
        return str(self)

class Select(Query):
    def __init__(self, child: Query, f: Callable[[Any], bool]) -> None:
        self.child = child
        self.f = f

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        return {t for t in self.child.eval(db) if self.f(t)}

    def __str__(self) -> str:
        return f'Select({self.child}, {self.f})'

    def __repr__(self) -> str:
        return str(self)

class Project(Query):
    def __init__(self, child: Query, indexes: List[int]) -> None:
        self.child = child
        self.indexes = indexes

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        return {[t[i] for i in self.indexes] for t in self.child.eval(db)}

    def __str__(self) -> str:
        return f'Project({self.child}, {self.indexes})'

    def __repr__(self) -> str:
        return str(self)

class Cross(Query):
    def __init__(self, lhs: Query, rhs: Query) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        return {lhs + rhs
                for lhs in self.lhs.eval(db)
                for rhs in self.rhs.eval(db)}

    def __str__(self) -> str:
        return f'Cross({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

class Cup(Query):
    def __init__(self, lhs: Query, rhs: Query) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        return self.lhs.eval(db) | self.rhs.eval(db)

    def __str__(self) -> str:
        return f'Cup({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

class Diff(Query):
    def __init__(self, lhs: Query, rhs: Query) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def eval(self, db: Dict[str, Set[Any]]) -> Set[Any]:
        return self.lhs.eval(db) - self.rhs.eval(db)

    def __str__(self) -> str:
        return f'Diff({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

class DbCreateRequest(NamedTuple):
    r: str
    arity: int

    def __str__(self) -> str:
        return f'create({self.r}({self.arity}))'

    def __repr__(self) -> str:
        return str(self)

class DbCreateReply(NamedTuple):
    success: bool

    def __str__(self) -> str:
        return f'{self.success}'

    def __repr__(self) -> str:
        return str(self)

class DbInsertRequest(NamedTuple):
    r: str
    t: List[str]

    def __str__(self) -> str:
        return f'insert({self.r}({tuple(self.t)}))'

    def __repr__(self) -> str:
        return str(self)

class DbInsertReply(NamedTuple):
    success: bool

    def __str__(self) -> str:
        return f'{self.success}'

    def __repr__(self) -> str:
        return str(self)

class DbDeleteRequest(NamedTuple):
    r: str
    t: List[str]

    def __str__(self) -> str:
        return f'insert({self.r}(tuple({self.t})))'

    def __repr__(self) -> str:
        return str(self)

class DbDeleteReply(NamedTuple):
    success: bool

    def __str__(self) -> str:
        return f'{self.success}'

    def __repr__(self) -> str:
        return str(self)

class DbQueryRequest(NamedTuple):
    q: Query

    def __str__(self) -> str:
        return f'q'

    def __repr__(self) -> str:
        return str(self)

class DbQueryReply(NamedTuple):
    result: Optional[Set[Any]]

    def __str__(self) -> str:
        return f'{self.result}'

    def __repr__(self) -> str:
        return str(self)

State = Dict[str, Set[Any]]
Input = Union[DbCreateRequest, DbInsertRequest, DbDeleteRequest, DbQueryRequest]
Output = Union[DbCreateReply, DbInsertReply, DbDeleteReply, DbQueryReply]
class Db(StateMachine[State, Input, Output]):
    def __init__(self):
        self.db: State = dict()

    def create(self, r: str, arity: int) -> DbCreateRequest:
        return DbCreateRequest(r, arity)

    def insert(self, r: str, t: List[str]) -> DbInsertRequest:
        return DbInsertRequest(r, t)

    def delete(self, r: str, t: List[str]) -> DbDeleteRequest:
        return DbDeleteRequest(r, t)

    def query(self, q: Query) -> DbQueryRequest:
        return DbQueryRequest(q)

    # override.
    def reset(self) -> None:
        self.db = dict()

    # override.
    def transition(self, i: Input) -> Output:
        if isinstance(i, DbCreateRequest):
            if i.r in self.db:
                return DbCreateReply(False)
            else:
                self.db[i.r] = set()
                return DbCreateReply(True)
        if isinstance(i, DbInsertRequest):
            if i.r not in self.db:
                return DbInsertReply(False)
            else:
                self.db[i.r].add(tuple(i.t))
                return DbInsertReply(True)
        if isinstance(i, DbDeleteRequest):
            if i.r not in self.db:
                return DbDeleteReply(False)
            else:
                self.db[i.r].remove(tuple(i.t))
                return DbDeleteReply(True)
        if isinstance(i, DbQueryRequest):
            try:
                return DbQueryReply(i.q.eval(self.db))
            except QueryException:
                return DbQueryReply(None)
        else:
            raise ValueError(f'Unrecognized input "{i}".')

    # override.
    def state(self) -> State:
        return self.db
