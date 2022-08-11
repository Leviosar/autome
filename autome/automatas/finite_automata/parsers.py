import json

from autome.automatas.finite_automata import (
    State,
    Transition,
    DeterministicFiniteAutomata,
    NonDeterministicFiniteAutomata,
    transition,
)
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Callable, Dict, List, Union


class JFlapConverter:
    @classmethod
    def parse(
        cls, source: Path, deterministic=True
    ) -> Union[NonDeterministicFiniteAutomata, DeterministicFiniteAutomata]:
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
            return NonDeterministicFiniteAutomata(
                states=states, transitions=transitions
            )

    @classmethod
    def save(cls, source: DeterministicFiniteAutomata, output_path: Path) -> bool:
        root = ET.Element("structure")
        type = ET.SubElement(root, "type")
        type.text = "fa"
        automaton = ET.SubElement(root, "automaton")

        for index, state in enumerate(source.states):
            _state = ET.SubElement(automaton, "state")
            _state.set("name", str(state.name))
            _state.set("id", str(state.id))
            ET.SubElement(_state, "x").text = f"{index * 30}"
            ET.SubElement(_state, "y").text = "50"

            if state.accept:
                ET.SubElement(_state, "final")

            if state.initial:
                ET.SubElement(_state, "initial")

        for index, transition in enumerate(source.transitions):
            _transition = ET.SubElement(automaton, "transition")
            ET.SubElement(_transition, "from").text = str(transition.origin.id)
            ET.SubElement(_transition, "to").text = str(transition.destiny.id)
            ET.SubElement(_transition, "read").text = transition.symbol

        document = ET.ElementTree(root)

        with open(output_path, "wb") as file:
            document.write(file, encoding="utf8", xml_declaration=True)
            return True

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
    def parse(
        cls, source: Union[Path, Dict], deterministic=True
    ) -> Union[NonDeterministicFiniteAutomata, DeterministicFiniteAutomata]:
        """
        Creates an instance of Machine parsed from a json file located at @path that follows the schematics provided by the project (see /machines folder)

        Throws FileNotFoundError if there's no file at @path
        Throws ValueError if the json file doesn't match the schematics
        """

        if isinstance(source, Dict):
            model = source
        elif isinstance(source, Path):
            with open(source, "r", encoding="utf8") as file:
                model = json.loads(file.read())

        states = [State.from_json(state) for state in model["states"]]
        transitions = [
            Transition.from_json(transition, states)
            for transition in model["transitions"]
        ]

        if deterministic:
            return DeterministicFiniteAutomata(states=states, transitions=transitions)
        else:
            return NonDeterministicFiniteAutomata(
                states=states, transitions=transitions
            )

    @classmethod
    def serialize(
        cls, source: Union[DeterministicFiniteAutomata, NonDeterministicFiniteAutomata]
    ) -> Dict:
        model = {}
        model["states"] = [state.to_json() for state in source.states]
        model["transitions"] = [
            transition.to_json() for transition in source.transitions
        ]

        return model

    @classmethod
    def save(
        cls,
        source: Union[DeterministicFiniteAutomata, NonDeterministicFiniteAutomata],
        output: Path,
    ):
        model = cls.serialize(source)

        with open(output, "w+") as fp:
            fp.write(json.dumps(model))

        print(f"Automato salvo em {output}")
