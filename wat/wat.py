from itertools import chain, combinations
from typing import Generator, Generic, Iterable, List, Set, Tuple, TypeVar

from .state_machine import StateMachine

State = TypeVar('State')
Input = TypeVar('Input')
Output = TypeVar('Output')
Trace = List[Tuple[Input, Output]]
EnumeratedTrace = List[Tuple[int, Input, Output]]

def _enumerate_trace(trace: Trace) -> EnumeratedTrace:
    return [(j, i, o) for (j, (i, o)) in enumerate(trace)]

def _unenumerate_trace(enumerated_trace: EnumeratedTrace) -> Trace:
    return [(i, o) for (j, i, o) in enumerated_trace]

# https://docs.python.org/3/library/itertools.html#recipes
T = TypeVar('T')
def _powerset(iterable: Iterable[T],
              min_size: int = 0) \
              -> Generator[List[T], None, None]:
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    sizes = range(min_size, len(s) + 1)
    for t in chain.from_iterable(combinations(s, r) for r in sizes):
        yield list(t)

def _subtraces(trace: EnumeratedTrace) \
               -> Generator[EnumeratedTrace, None, None]:
    indexes = range(len(trace))
    for index_set in _powerset(indexes):
        yield [trace[i] for i in sorted(index_set)]

def _supertraces(subtrace: EnumeratedTrace, trace: EnumeratedTrace) \
                 -> Generator[EnumeratedTrace, None, None]:
    subtrace_index_set = set(j for (j, _, _) in subtrace)
    indexes = range(len(trace))
    for index_set in _powerset(indexes, min_size=len(subtrace)):
        if subtrace_index_set <= set(index_set):
            yield [trace[j] for j in sorted(index_set)]

def _trace_happens_before(a: EnumeratedTrace, b: EnumeratedTrace) -> bool:
    (j, _, _) = a[-1]
    (k, _, _) = b[0]
    return j < k

def _trace_satisfies_io(m: StateMachine[State, Input, Output],
                        trace: EnumeratedTrace,
                        io: Tuple[Input, Output]) \
                        -> bool:
    i, o = io
    m.run([i for (_, i, _) in trace])
    return o == m.transition(i)

def _subtrace_closed_under_superset(m: StateMachine[State, Input, Output],
                                    subtrace: EnumeratedTrace,
                                    trace: EnumeratedTrace,
                                    io: Tuple[Input, Output]) \
                                    -> bool:
    return all(_trace_satisfies_io(m, supertrace, io) for
               supertrace in _supertraces(subtrace, trace))

def _subtrace_is_witness(m: StateMachine[State, Input, Output],
                         subtrace: EnumeratedTrace,
                         trace: EnumeratedTrace,
                         io: Tuple[Input, Output]) \
                         -> bool:
    if not _subtrace_closed_under_superset(m, subtrace, trace, io):
        return False

    return all(subsubtrace == subtrace or
               not _subtrace_closed_under_superset(m, subsubtrace, trace, io)
               for subsubtrace in _subtraces(subtrace))

def _enumerated_wat(m: StateMachine[State, Input, Output],
                    trace: EnumeratedTrace,
                    io: Tuple[Input, Output]) \
                    -> List[EnumeratedTrace]:
    witnesses = [subtrace
                 for subtrace in _subtraces(trace)
                 if _subtrace_is_witness(m, subtrace, trace, io)]
    return [witness
            for witness in witnesses
            if not any(w != witness and _trace_happens_before(witness, w)
                       for w in witnesses)]

def wat(m: StateMachine[State, Input, Output],
        trace: Trace,
        j: int) \
        -> List[EnumeratedTrace]:
    enumerated_trace = _enumerate_trace(trace[:j])
    i, o = trace[j]
    return _enumerated_wat(m, enumerated_trace, (i, o))
