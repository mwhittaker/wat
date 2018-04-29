from typing import (Callable, Dict, List, NamedTuple, FrozenSet, Optional, Set,
                    Tuple, Union)

from .state_machine import StateMachine

# Types ########################################################################
# TODO: Document.
class Timestamp(NamedTuple):
    tick: int
    step: int

    def increment_tick(self) -> 'Timestamp':
        return Timestamp(self.tick + 1, 0)

    def increment_step(self) -> 'Timestamp':
        return Timestamp(self.tick, self.step + 1)

Record = Tuple[str, ...]

class TimestampedRecord(NamedTuple):
    record: Record
    timestamp: Timestamp

class RecordId(NamedTuple):
    relation_name: str
    record: Record
    timestamp: Timestamp

RelationName = str
Relation = Set[TimestampedRecord]
Arity = int
Schema = Dict[RelationName, Arity]
Database = Dict[RelationName, Relation]
Lineage = Set[FrozenSet[RecordId]]


# Queries ######################################################################
# Every output tuple is annotated with its witness.
WbQueryOutput = Set[Tuple[Record, FrozenSet[RecordId]]]
Coercible = Union[str, Record, 'WbQuery']

def coerce(coercible: Coercible) -> 'WbQuery':
    if isinstance(coercible, str):
        return WbRelation(coercible)
    if isinstance(coercible, tuple):
        return WbRecord(coercible)
    elif isinstance(coercible, WbQuery):
        return coercible
    else:
        raise ValueError(f'Unexpected coercible "{coercible}".')

class WbQuery:
    def eval(self, db: Database) -> WbQueryOutput:
        raise NotImplementedError()

    def __add__(self, other: Coercible) -> 'WbCup':
        return WbCup(self, coerce(other))

    def __radd__(self, other: Coercible) -> 'WbCup':
        return WbCup(coerce(other), self)

    def __sub__(self, other: Coercible) -> 'WbDiff':
        return WbDiff(self, coerce(other))

    def __rsub__(self, other: Coercible) -> 'WbDiff':
        return WbDiff(coerce(other), self)

    def __mul__(self, other: Coercible) -> 'WbCross':
        return WbCross(self, coerce(other))

    def __rmul__(self, other: Coercible) -> 'WbCross':
        return WbCross(coerce(other), self)

    def select(self, f: Callable[[Record], bool]) -> 'WbSelect':
        return WbSelect(self, f)

    def project(self, indexes: List[int]) -> 'WbProject':
        return WbProject(self, indexes)

class WbRecord(WbQuery):
    def __init__(self, record: Record) -> None:
        self.record = record

    def eval(self, db: Database) -> WbQueryOutput:
        return {(self.record, frozenset())}

    def __str__(self) -> str:
        return f'{self.record}'

    def __repr__(self) -> str:
        return str(self)

class WbRelation(WbQuery):
    def __init__(self, R: RelationName) -> None:
        self.R = R

    def eval(self, db: Database) -> WbQueryOutput:
        assert self.R in db, (self.R, db)
        return {(r, frozenset([RecordId(self.R, r, t)]))
                for (r, t) in db[self.R]}

    def __str__(self) -> str:
        return f'{self.R}'

    def __repr__(self) -> str:
        return str(self)

class WbSelect(WbQuery):
    def __init__(self, child: Coercible, f: Callable[[Record], bool]) -> None:
        self.child = coerce(child)
        self.f = f

    def eval(self, db: Database) -> WbQueryOutput:
        return {(r, lineage) for r, lineage in self.child.eval(db) if self.f(r)}

    def __str__(self) -> str:
        return f'Select({self.child}, {self.f})'

    def __repr__(self) -> str:
        return str(self)

class WbProject(WbQuery):
    def __init__(self, child: Coercible, indexes: List[int]) -> None:
        self.child = coerce(child)
        self.indexes = indexes

    def eval(self, db: Database) -> WbQueryOutput:
        return {(tuple(r[i] for i in self.indexes), lineage)
                 for r, lineage in self.child.eval(db)}

    def __str__(self) -> str:
        return f'Project({self.child}, {self.indexes})'

    def __repr__(self) -> str:
        return str(self)

class WbCross(WbQuery):
    def __init__(self, lhs: Coercible, rhs: Coercible) -> None:
        self.lhs = coerce(lhs)
        self.rhs = coerce(rhs)

    def eval(self, db: Database) -> WbQueryOutput:
        return {(lhs_r + rhs_r, lhs_lineage | rhs_lineage)
                for (lhs_r, lhs_lineage) in self.lhs.eval(db)
                for (rhs_r, rhs_lineage) in self.rhs.eval(db)}

    def __str__(self) -> str:
        return f'Cross({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

class WbCup(WbQuery):
    def __init__(self, lhs: Coercible, rhs: Coercible) -> None:
        self.lhs = coerce(lhs)
        self.rhs = coerce(rhs)

    def eval(self, db: Database) -> WbQueryOutput:
        return self.lhs.eval(db) | self.rhs.eval(db)

    def __str__(self) -> str:
        return f'Cup({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

class WbDiff(WbQuery):
    def __init__(self, lhs: Coercible, rhs: Coercible) -> None:
        self.lhs = coerce(lhs)
        self.rhs = coerce(rhs)

    def eval(self, db: Database) -> WbQueryOutput:
        rhs_records = {r for r, _ in self.rhs.eval(db)}
        return {(r, lineage)
                for (r, lineage) in self.lhs.eval(db)
                if r not in rhs_records}

    def __str__(self) -> str:
        return f'Diff({self.lhs}, {self.rhs})'

    def __repr__(self) -> str:
        return str(self)

# White Box ####################################################################
class Rule(NamedTuple):
    relation_name: RelationName
    query: WbQuery

class Input(NamedTuple):
    relation_name: RelationName
    record: Record

class Output(NamedTuple):
    reply: Set[Record]

EnumeratedTrace = List[Tuple[int, Input, Output]]

class WhiteBox(StateMachine[Input, Output]):
    def __init__(self) -> None:
        self.timestamp = Timestamp(0, 0)
        self.schema: Schema = dict()
        self.db: Database = dict()
        self.rules: Dict[RelationName, List[Rule]] = dict()
        self.lineage: Dict[RecordId, Lineage] = dict()
        self.inputs: Dict[int, Input] = dict()
        self.outputs: Dict[int, Output] = dict()
        self.output_lineage: Dict[int, Dict[RecordId, Lineage]] = dict()

    def create_table(self, name: RelationName, arity: Arity) -> None:
        assert name not in self.schema, (name, self.schema)
        self.schema[name] = arity
        self.db[name] = set()

    def register_rules(self, name: RelationName, rules: List[Rule]) -> None:
        assert name not in self.rules, (name, self.rules)
        assert len(rules) > 0, rules
        self.rules[name] = rules

    def _flatten_lineage(self, lineage: Lineage) -> Set[RecordId]:
        output: Set[RecordId] = set()
        for witness in lineage:
            for rid in witness:
                if rid.timestamp.step == 0:
                    output.add(rid)
                else:
                    output |= self._flatten_lineage(self.lineage[rid])
        return output

    def get_output_lineage(self, j: int) -> Dict[RecordId, EnumeratedTrace]:
        assert j in self.output_lineage, (j, self.output_lineage)

        ans: Dict[RecordId, EnumeratedTrace] = dict()
        for rid, lineage in self.output_lineage[j].items():
            rids = self._flatten_lineage(lineage)
            indexes = sorted(rid.timestamp.tick
                             for rid in rids
                             if rid.timestamp.tick != j)
            ans[rid] = [(j, self.inputs[j], self.outputs[j]) for j in indexes]
        return ans

    # override.
    def reset(self) -> None:
        self.timestamp = Timestamp(0, 0)
        self.db = {name: set() for name in self.schema}
        self.lineage = dict()

    # override.
    def transition(self, i: Input) -> Output:
        assert i.relation_name in self.schema, (i.relation_name, self.schema)
        assert i.relation_name in self.rules, (i.relation_name, self.rules)
        assert len(i.record) == self.schema[i.relation_name]

        # Save the input.
        self.inputs[self.timestamp.tick] = i

        # Add the request to the request table.
        tr = TimestampedRecord(i.record, self.timestamp)
        self.db[i.relation_name].add(tr)

        # Run all but the last rule.
        for name, query in self.rules[i.relation_name][:-1]:
            # Increment the step before each step.
            self.timestamp = self.timestamp.increment_step()

            # Run the query.
            ans = query.eval(self.db)
            records = {r for r, lineage in ans}

            # Clear the relation being written into.
            self.db[name] = {tr for tr in self.db[name]
                                if tr.record in records}

            for r, lineage in ans:
                # Record the record.
                tr = TimestampedRecord(r, self.timestamp)
                self.db[name].add(tr)

                # Record the lineage.
                rid = RecordId(name, r, self.timestamp)
                if rid not in self.lineage:
                    self.lineage[rid] = set()
                self.lineage[rid].add(lineage)

        # Run the last query.
        name, query = self.rules[i.relation_name][-1]
        self.timestamp = self.timestamp.increment_step()
        ans = query.eval(self.db)

        # Store the output's lineage.
        output_lineage: Dict[RecordId, Lineage] = dict()
        for r, lineage in ans:
            rid = RecordId(name, r, self.timestamp)
            if rid not in output_lineage:
                output_lineage[rid] = set()
            output_lineage[rid].add(lineage)
        self.output_lineage[self.timestamp.tick] = output_lineage

        # Compute and cache the output.
        output = Output({r for r, lineage in ans})
        self.outputs[self.timestamp.tick] = output

        # Increment the tick.
        self.timestamp = self.timestamp.increment_tick()

        # Clear the request table.
        self.db[i.relation_name] = set()

        return output
