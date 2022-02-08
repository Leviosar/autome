from copy import deepcopy

from autome.state import State
from autome.transition import Transition
from autome.base_machine import BaseMachine
from autome.utils import Direction

class FiniteAutomata(BaseMachine):
    """
    Finite automata, accepts states and transitions as inputs. Upon reaching a non-deterministic transition
    the machine will split into multiple branches of computation (beware with the big bad recursion) and
    will accept the input if any of the branches stop into a final state.

    An automata can only have one initial state, but it may have multiple acceptance and reject states. Computation will be stopped as soon as the machine reaches one of those two types of state.
    """
    def __init__(self, states=[], transitions=[]) -> None:
        self.states: List[State] = states
        self.current_state = next(filter(lambda state: state.initial, self.states))

        assert self.current_state is not None, "Automato sem estado inicial"


    def execute_transition(self, transition: Transition) -> None:
        """
        Executes a transition into the automata, moving reading head to the right and applying changes to the current state.
        """
        self.current_state = transition.destiny


    def accepts(self, word: str) -> bool:
        """
        Resets the finite automata to an initial state and runs the computation for a given word.
        """
        self.current_state = next(filter(lambda state: state.initial, self.states))

        for character in word:
            if !self.step():
                return False

        return self.current_state.accept
    

    def step(self) -> bool:
        """
        Runs one step of the computation for the current finite automata.

        The step will take the current symbol from the reading head, compare with the list
        of available transitions trying to find a match. If it doesn't find, the machine will
        be pushed into a rejection state, where the computation will stop.

        However, if it does find a match shifts the current state of the machine
        to the destiny of the found transition and moves the reading head.
        """

        condition: Callable[[Transition], bool] = (
            lambda transition: symbols == transition.reads
            and self.current_state == transition.origin
        )

        matches = filter(condition, self.transitions)

        if (len(matches) == 0):
            return False
        else:
            self.execute_transition(next(matches))
            return True


    def complement(self) -> 'FiniteAutomata':
        new = deepcopy(self)
        new.states = list(map(lambda state: state.accepts = !state.accepts, new.states))
        return new

    
    def union(self, other) -> 'FiniteAutomata':
        old_initials = [self.initial, other.initial] # Old initial states from self and other
        old_finals = [...self.final, ...other.final] # Old final states from self and other

        new_final = State('qnf', 'qnf', final=True)
        new_initial = State('qni', 'qni', initial=True)

        states = [newFinal, newInitial] + [...self.states, ...other.states] 
        
        # From the new initial state, creates an epsilon transition to all the old initial states
        new_to_old_initial = [
            Transition(new_initial, old_initial, ['&'], ['&'], []) 
            for old_initial in old_initials
        ]

        # From the old final states, creates and epsilon transition to the new final state 
        old_to_new_final = [
            Transition(old_final, new_final, ['&'], ['&'], [])
            for old_final in old_finals
        ]

        transitions = [
            ...self.transitions, 
            ...other.transitions,
            ...new_to_old_initial,
            ...old_to_new_final
        ]

        # Because we have epsilon transitions, the resultant is a NDFA
        # that should be determinized before used
        new = NDFiniteAutomata(
            states=states,
            transitions=transitions
        ).determinize()

        return new


    def intersection(self, other) -> 'FiniteAutomata':
        a = self.complement()
        b = self.complement()

        # Still needs to implement union kekw
        result = a.union(b).complement()

        for state in result.states:
            if state.accepts and state.initial:
                state.accepts = False

        return result


    # Dunder methods to allow operator overloading
    def __or__(self, other):
        return self.union(self, other)


    def __and__(self, other):
        return self.intersection(self, other)


    def __invert__(self):
        return self.complement()