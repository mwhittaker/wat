from typing import List, Tuple, TypeVar, Generic

Input = TypeVar('Input')
Output = TypeVar('Output')

class StateMachine(Generic[Input, Output]):
    """A deterministic state machine.

    A StateMachine represents a determinstic state machine. A StateMachine
    begins in an initial start state. Upon receiving an input of type Input,
    the state machine transitions into a new state and outputs an output of
    type Output.
    """

    def reset(self) -> None:
        """Resets the state machine to its start state."""
        raise NotImplementedError()

    def transition(self, i: Input) -> Output:
        """Transitions to a new state and outputs and ouput."""
        raise NotImplementedError()

    def run(self, inputs: List[Input]) -> List[Tuple[Input, Output]]:
        """Performs a sequence of transitions from the start state."""
        self.reset()
        trace: List[Tuple[Input, Output]] = []
        for i in inputs:
            o = self.transition(i)
            trace.append((i, o))
        return trace
