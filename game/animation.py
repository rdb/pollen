from wecs.core import Component, System, and_filter
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


class AnimationPlayer(System):
    entity_filters = {
        'character': and_filter([Character]),
    }

    def change_state(self, char, old_state, new_state):
        old_state_def = char.states.get(old_state, {})
        new_state_def = char.states[new_state]

        transition = char.transitions.get((old_state, new_state))
        if transition:
            for part, anim in old_state_def.items():
                if part not in new_state_def and part not in transition:
                    char._actor.stop(anim, partName=part)

            for part, anim in transition.items():
                loop_anim = new_state_def.get(part)
                char._actor.set_play_rate(char.play_rate, anim, partName=part)
                if loop_anim:
                    char._actor.set_play_rate(char.play_rate, loop_anim, partName=part)
                    Sequence(
                        char._actor.actorInterval(anim, partName=part),
                        Func(lambda: char._actor.loop(loop_anim, partName=part)),
                    ).start()
                else:
                    char._actor.actorInterval(anim, partName=part).start()

            for part, anim in new_state_def.items():
                if part not in transition:
                    if part not in old_state_def or old_state_def[part] != anim:
                        char._actor.loop(anim, partName=part)
        else:
            for part, anim in old_state_def.items():
                if part not in new_state_def:
                    char._actor.stop(anim, partName=part)

            for part, anim in new_state_def.items():
                if part not in old_state_def or old_state_def[part] != anim:
                    char._actor.set_play_rate(char.play_rate, anim, partName=part)
                    char._actor.loop(anim, partName=part)

    def update(self, entities_by_filter):
        for entity in entities_by_filter['character']:
            char = entity[Character]

            if char._state != char.state:
                self.change_state(char, char._state, char.state)
                char._state = char.state
