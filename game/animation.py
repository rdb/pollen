from wecs.core import Component, System, and_filter
from panda3d import core
from dataclasses import field

from direct.interval.IntervalGlobal import Sequence, Func


@Component()
class Character:
    state: str
    play_rate: float = 1.0

    states: dict = field(default_factory=dict)
    transitions: dict = field(default_factory=dict)
    subparts: dict = field(default_factory=dict)

    _state = None
    _state_paths: dict = field(default_factory=dict)


class AnimationPlayer(System):
    entity_filters = {
        'character': and_filter([Character]),
    }

    def change_state(self, char, old_state, new_state):
        old_state_def = char.states.get(old_state, {})
        new_state_def = char.states[new_state]

        char._actor.stop()
        if old_state is not None:
            char._state_paths[old_state].stash()

        transition = char.transitions.get((old_state, new_state))
        if transition:
            char._actor.unstash()

            for part, anim in transition.items():
                Sequence(
                    char._actor.actor_interval(anim, partName=part, playRate=char.play_rate),
                    Func(lambda: char._actor.stash()),
                    Func(lambda: char._state_paths[new_state].unstash()),
                ).start()
        else:
            char._actor.stash()
            char._state_paths[new_state].unstash()

    def update(self, entities_by_filter):
        for entity in entities_by_filter['character']:
            char = entity[Character]

            if char._state != char.state:
                self.change_state(char, char._state, char.state)
                char._state = char.state
