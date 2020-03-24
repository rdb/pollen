from wecs.core import Component, System, and_filter
from dataclasses import field


@Component()
class Character:
    animations: dict = field(default_factory=dict)
    subparts: dict = field(default_factory=dict)


@Component()
class Animation:
    playing: set = field(default_factory=set)
    _playing: set = field(default_factory=set)

    def play(self, anim):
        self.playing.add(anim)

    def stop(self, anim):
        self.playing.discard(anim)


class AnimationPlayer(System):
    entity_filters = {
        'character': and_filter([Character]),
        'anim_char': and_filter([Character, Animation]),
    }

    def update(self, entities_by_filter):
        for entity in entities_by_filter['anim_char']:
            char = entity[Character]
            anim = entity[Animation]

            stop_anims = anim._playing - anim.playing
            for anim3 in stop_anims:
                for part, anim2 in char.animations[anim3]:
                    char._actor.stop(anim2, partName=part)

            start_anims = anim.playing - anim._playing
            for anim3 in start_anims:
                for part, anim2 in char.animations[anim3]:
                    char._actor.loop(anim2, partName=part)
                    char._actor.setPlayRate(0.5, anim2, partName=part)

            anim._playing = anim.playing
