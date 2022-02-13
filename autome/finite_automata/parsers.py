import json
from autome.finite_automata import State, Transition, DeterministicFiniteAutomata, NonDeterministicFiniteAutomata
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Callable, List, Union


class JFlapConverter:
    @classmethod
    def parse(cls, source: Path, deterministic=True) -> Union[NonDeterministicFiniteAutomata, DeterministicFiniteAutomata]:
        """
        Converts a .jff file into a Finite State Automata. Some serious shit may happen if you manually edit the .jff file, don't do it.
        """
        tree = ET.parse(source)
        root = tree.getroot()
        automaton: ET.Element = root.find("./automaton")
        
        state_models: List[ET.Element] = automaton.findall("./state")
        states: List[State] = list(map(JFlapConverter.__parse_state__, state_models))
        
        transition_models: List[ET.Element] = automaton.findall("./transition")
        
        transitions = []
        for model in transition_models:
            transitions.append(JFlapConverter.__parse_transition__(model, states))
            
        if deterministic:
            return DeterministicFiniteAutomata(states=states, transitions=transitions)
        else:
            return NonDeterministicFiniteAutomata(states=states, transitions=transitions)

    @classmethod
    def __parse_state__(cls, model: ET.Element) -> State:
        label = model.attrib["id"]
        initial = len(model.findall("./initial")) > 0
        accept = len(model.findall("./final")) > 0
        return State(label, initial=initial, accept=accept)

    @classmethod
    def __parse_transition__(cls, model: ET.Element, states: List[State]) -> Transition:
        origin_id = model.find("./from").text
        destiny_id = model.find("./to").text

        origin = next(filter(lambda state: state.name == origin_id, states))
        destiny = next(filter(lambda state: state.name == destiny_id, states))
        reads = model.findall("./read")[0].text
        
        return Transition(origin, destiny, reads)


class JSONConverter:
    @classmethod
    def parse(cls, source: Path, deterministic=True) -> Union[NonDeterministicFiniteAutomata, DeterministicFiniteAutomata]:
        """
        Creates an instance of Machine parsed from a json file located at @path that follows the schematics provided by the project (see /machines folder)

        Throws FileNotFoundError if there's no file at @path
        Throws ValueError if the json file doesn't match the schematics
        """
        
        with open(source, "r", encoding="utf8") as file:
            model = json.loads(file.read())
            states = [State.parse(state) for state in model["states"]]
            transitions = [
                Transition.parse(transition, states)
                for transition in model["transitions"]
            ]

        if deterministic:
            return DeterministicFiniteAutomata(states=states, transitions=transitions)
        else:
            return NonDeterministicFiniteAutomata(states=states, transitions=transitions)