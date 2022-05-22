from copy import deepcopy
from mimetypes import init
import pdb
from turtle import pd
from tabulate import tabulate
from typing import Callable, List, Set, Tuple

from autome.finite_automata.state import State
from autome.finite_automata.transition import Transition
from autome.base_machine import BaseMachine


class DeterministicFiniteAutomata(BaseMachine):
    """
    Finite automata, accepts states and transitions as inputs.

    An automata can only have one initial state, but it may have multiple acceptance states.
    """

    def __init__(
        self, states=[], transitions=[], title="FiniteAutomata", description=""
    ) -> None:
        self.states: List[State] = list(states)
        self.transitions: List[Transition] = list(transitions)
        self.title = title
        self.description = description
        self.create_transition_map()

    def create_transition_map(self):
        self.transition_map = dict()

        for state in self.states:
            if state not in self.transition_map:
                self.transition_map[state] = {}

            for transition in self.transitions:
                if transition.origin == state:
                    if transition.symbol not in self.transition_map[state]:
                        self.transition_map[state][transition.symbol] = set()
                    self.transition_map[state][transition.symbol].add(
                        transition.destiny
                    )

    def add_transition(self, origin: State, destiny: State, symbol: str) -> None:
        """Adds a new transition the the automata

        Args:
            origin (State): state from which the transition starts
            destiny (State): state where the transition ends
            symbol (str): trigger symbol of the transition
        """

        self.transitions = list(
            set(
                self.transitions
                + [Transition(origin=origin, destiny=destiny, symbol=symbol)]
            )
        )

    def add_state(self, state: State) -> None:
        """Adds a new state the the automata

        Args:
            state (State): new state
        """

        self.states = list(set(self.states + [state]))

    def execute_transition(self, transition: Transition) -> None:
        """
        Executes a transition into the automata, moving reading head to the right and applying changes to the current state.
        """
        self.current_state = transition.destiny

    def final(self) -> List[State]:
        return list(filter(lambda state: state.accept, self.states))

    def initial(self) -> State:
        return next(filter(lambda state: state.initial, self.states))

    def accepts(self, word: str) -> bool:
        """
        Resets the finite automata to an initial state and runs the computation for a given word.
        """
        self.current_state = self.initial()

        for character in word:
            result = self.step(character)
            print(result)
            input()
            if not result:
                return False

        print(self.current_state)

        return self.current_state.accept

    def step(self, character) -> bool:
        """
        Runs one step of the computation for the current finite automata.

        The step will take the current symbol from the reading head, compare with the list
        of available transitions trying to find a match. If it doesn't find, the machine will
        be pushed into a rejection state, where the computation will stop.

        However, if it does find a match shifts the current state of the machine
        to the destiny of the found transition and moves the reading head.
        """

        condition: Callable[[Transition], bool] = (
            lambda transition: character == transition.symbol
            and self.current_state == transition.origin
        )

        matches = list(filter(condition, self.transitions))

        if len(list(matches)) == 0:
            return False
        else:
            self.execute_transition(matches[0])
            return True

    def complement(self) -> "DeterministicFiniteAutomata":
        """Generate the complement of a given automata. The algorithm is pretty straight-forward, just note
        that we had to use Python's deepcopy to create a new object exactly equal to the old one but with different
        memory address

        Returns:
            DeterministicFiniteAutomata: a new automata, representing the complement of the operand
        """
        new = deepcopy(self)

        for state in new.states:
            state.accept = not state.accept

        return new

    def union(
        self, other: "DeterministicFiniteAutomata"
    ) -> "DeterministicFiniteAutomata":
        """Generate an union between the AF, the original algorithm returns a NDFA, but for use purposes
        we're determinizing the resulting machine before returning

        Returns:
            DeterministicFiniteAutomata: a new automata, representing the union between operands
        """

        old_initials = (
            self.initial(),
            other.initial(),
        )  # Old initial states from self and other
        old_finals = (
            self.final() + other.final()
        )  # Old final states from self and other

        new_final = State("qnf", accept=True)
        new_initial = State("qni", initial=True)

        states = [new_final, new_initial] + self.states + other.states

        for state in states:
            if state != new_initial:
                state.initial = False

        # From the new initial state, creates an epsilon transition to all the old initial states
        new_to_old_initial = [
            Transition(new_initial, old_initial, "&") for old_initial in old_initials
        ]

        # From the old final states, creates and epsilon transition to the new final state
        old_to_new_final = [
            Transition(old_final, new_final, "&") for old_final in old_finals
        ]

        transitions = (
            self.transitions + other.transitions + new_to_old_initial + old_to_new_final
        )

        # Because we have epsilon transitions, the resultant is a NDFA
        # that should be determinized before used
        new = NonDeterministicFiniteAutomata(states=states, transitions=transitions)
        new.create_transition_map()

        return new.determinize()

    def cross_union(
        self, other: "DeterministicFiniteAutomata"
    ) -> "DeterministicFiniteAutomata":
        result = NonDeterministicFiniteAutomata()

        initial = State("q0", initial=True)
        result.add_state(initial)

        state_mapping = {}
        index = 1

        for state in sorted(self.states):
            state_mapping[state] = State(f"q{index}", accept=state.accept)
            result.add_state(state_mapping[state])
            index += 1

        result.create_transition_map()

        symbols = list(set(map(lambda transition: transition.symbol, self.transitions)))
        symbols.sort()

        for state in sorted(self.states):
            for symbol in symbols:
                if symbol in self.transition_map[state]:
                    destiny_states = self.transition_map[state][symbol]
                    for destiny_state in destiny_states:
                        result.add_transition(
                            state_mapping[state], state_mapping[destiny_state], symbol
                        )

        result.add_transition(initial, state_mapping[self.initial()], "&")

        state_mapping = {}

        for state in sorted(other.states):
            state_mapping[state] = State(f"q{index}", accept=state.accept)
            result.add_state(state_mapping[state])
            index += 1

        result.create_transition_map()

        symbols = list(set(map(lambda transition: transition.symbol, self.transitions)))
        symbols.sort()

        for state in sorted(other.states):
            for symbol in symbols:
                if symbol in other.transition_map[state]:
                    destiny_states = other.transition_map[state][symbol]
                    for destiny_state in destiny_states:
                        result.add_transition(
                            state_mapping[state], state_mapping[destiny_state], symbol
                        )

        result.add_transition(initial, state_mapping[other.initial()], "&")

        result.create_transition_map()

        # pdb.set_trace()

        return result.determinize()

    def intersection(
        self, other: "DeterministicFiniteAutomata"
    ) -> "DeterministicFiniteAutomata":
        """Generate an intersection of the given automatas, the algorithm actually uses other
        automata operation's to mount the new machine.

        Returns:
            DeterministicFiniteAutomata: a new automata, representing the intersection between operands
        """
        a = self.complement()
        b = other.complement()

        result = (a | b).complement()

        for state in result.states:
            if state.accept and state.initial:
                state.accept = False

        return result

    # Dunder methods to allow operator overloading
    def __or__(self, other):
        return self.cross_union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __invert__(self):
        return self.complement()

    def __repr__(self):
        symbols = list(set(map(lambda transition: transition.symbol, self.transitions)))
        symbols.sort()

        headers = ["state"] + list(symbols)

        data = []

        self.states.sort()

        for state in self.states:
            name = state.name

            if state.initial:
                name = "→" + name

            if state.accept:
                name = name + "*"

            aux = [name]

            for symbol in symbols:
                if symbol not in self.transition_map[state]:
                    aux.append("-")
                else:
                    aux.append(self.transition_map[state][symbol])
            data.append(aux)

        return tabulate(data, headers=headers, tablefmt="fancy_grid")

    def __eq__(self, other: "DeterministicFiniteAutomata") -> bool:
        for state in self.states:
            if state not in other.states:
                return False

        for transition in self.transitions:
            if transition not in other.transitions:
                return False

        return True


class NonDeterministicFiniteAutomata(DeterministicFiniteAutomata):
    def run(self, word):
        return self.determinize().run(word)

    def e_closure(self, states: List[State]) -> Tuple[Set[State], bool]:
        """Calculates the sigma-closure of a given list of states in the current automata
        also returning if the resulting sigma-closure is a new final state or not

        Args:
            states (List[State]): the states that will be merged

        Returns:
            Set[State]: sigma-closure set, containing all the states reached by &-transitions
            from the original states passed
        """
        closure = set()
        accept = False

        while states:
            state = states.pop()
            closure.add(state)

            if state.accept:
                accept = True

            if "&" in self.transition_map[state]:
                for destiny in self.transition_map[state]["&"]:
                    if destiny not in closure:
                        states.append(destiny)

        return (closure, accept)

    def determinize(self) -> "DeterministicFiniteAutomata":
        """Determinizes a NDFA, returning an equivalent DFA

        Returns:
            DeterministicFiniteAutomata: the equivalente DFA to the operand
        """
        symbols = list(set([transition.symbol for transition in self.transitions]))

        new = DeterministicFiniteAutomata()

        state_stack = [{state} for state in self.states]

        while state_stack:

            states = list(state_stack.pop())

            (state_closure, _) = self.e_closure(states)

            closure_state = State.join(list(state_closure))

            new.add_state(closure_state)

            for symbol in symbols:
                if symbol == "&":
                    continue

                transitions = set()

                for to_state in state_closure:
                    if symbol not in self.transition_map[to_state]:
                        continue
                    transitions.update(self.transition_map[to_state][symbol])

                if len(transitions) == 0:
                    continue

                (closure, _) = self.e_closure(list(transitions))

                new_state = State.join(list(closure))

                if not (new_state in new.states) and not (new_state in state_stack):
                    state_stack.append(closure)

                new.add_transition(closure_state, new_state, symbol)

        new.create_transition_map()

        return new
