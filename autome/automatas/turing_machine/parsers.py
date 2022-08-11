from autome.utils.enums import Direction
from os import read
from autome.automatas.turing_machine.tape import Tape
from autome.automatas.turing_machine.transition import Transition
from autome.automatas.turing_machine.state import State
from pathlib import Path
from xml.etree import ElementTree as ET
from autome.automatas.turing_machine.machine import Machine
from typing import Callable, List


class JFlapConverter:
    @classmethod
    def parse(cls, source: Path) -> Machine:
        """
        Converts a .jff (basic a XML) file into a Turing Machine. Some serious shit may happen if you manually edit the .jff file, don't do it.
        """
        tree = ET.parse(source)
        root = tree.getroot()
        automaton: ET.Element = root.find("./automaton")
        states: List[ET.Element] = automaton.findall("./state")
        transitions: List[ET.Element] = automaton.findall("./transition")

        states: List[State] = list(map(JFlapConverter.__parse_state__, states))

        transition_lambda: Callable[
            [ET.Element], Transition
        ] = lambda model: JFlapConverter.__parse_transition__(model, states)
        transitions: List[Transition] = list(map(transition_lambda, transitions))

        tape_amount = len(root.find("./automaton/transition").find("./read"))
        tapes = [Tape() for i in range(tape_amount)]

        return Machine(states=states, transitions=transitions, tapes=tapes)

    @classmethod
    def __parse_state__(cls, model: ET.Element) -> State:
        id = model.attrib["id"]
        label = model.attrib["name"]
        initial = len(model.findall("./initial")) > 0
        accept = len(model.findall("./final")) > 0
        return State(label, id, initial=initial, accept=accept)

    @classmethod
    def __parse_transition__(cls, model: ET.Element, states: List[State]) -> Transition:
        origin_id = model.find("./from").text
        destiny_id = model.find("./to").text

        origin = next(filter(lambda state: state.name == origin_id, states))
        destiny = next(filter(lambda state: state.name == destiny_id, states))
        reads = model.findall("./read")
        writes = model.findall("./write")
        moves = model.findall("./move")

        if len(reads) > 1:
            reads.sort(key=lambda item: item.attrib.get("tape"))
            writes.sort(key=lambda item: item.attrib.get("tape"))
            moves.sort(key=lambda item: item.attrib.get("tape"))

        reads = [item.text if item.text is not None else "_" for item in reads]
        writes = [item.text if item.text is not None else "_" for item in writes]
        moves = [Direction[item.text] for item in moves]

        return Transition(origin, destiny, reads, writes, moves)
