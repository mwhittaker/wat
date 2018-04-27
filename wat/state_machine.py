from typing import List, Tuple, TypeVar, Generic

State = TypeVar('State')
Input = TypeVar('Input')
Output = TypeVar('Output')

class StateMachine(Generic[State, Input, Output]):
    def reset(self) -> None:
        raise NotImplementedError()

    def transition(self, i: Input) -> Output:
        raise NotImplementedError()

    def state(self) -> State:
        raise NotImplementedError()

    def run(self, inputs: List[Input]) -> List[Tuple[Input, Output]]:
        self.reset()
        trace: List[Tuple[Input, Output]] = []
        for i in inputs:
            o = self.transition(i)
            trace.append((i, o))
        return trace

