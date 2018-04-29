from typing import List, Tuple, TypeVar, Generic

Input = TypeVar('Input')
Output = TypeVar('Output')

class StateMachine(Generic[Input, Output]):
    def reset(self) -> None:
        raise NotImplementedError()

    def transition(self, i: Input) -> Output:
        raise NotImplementedError()

    def run(self, inputs: List[Input]) -> List[Tuple[Input, Output]]:
        self.reset()
        trace: List[Tuple[Input, Output]] = []
        for i in inputs:
            o = self.transition(i)
            trace.append((i, o))
        return trace
