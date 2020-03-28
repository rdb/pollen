from direct.showbase.Audio3DManager import Audio3DManager
from direct.interval.SoundInterval import SoundInterval
from wecs.core import Component, System, and_filter
from panda3d import core
from dataclasses import field

from .camera import Camera
from .terrain import TerrainObject


MUSIC_FADE_TIME = 2.0


@Component()
class Listener:
    pass


@Component()
class Music:
    songs: list
    current: str = None

    _playing = None
    _active = None

    def play(self, song):
        assert song in self.songs
        self.current = song


@Component()
class SfxPlayer:
    sounds: list
    loop: bool = False
    volume: float = 1.0

    _queued: set = field(default_factory=set)

    def play(self, sound):
        self._queued.add(sound)


class AudioSystem(System):
    entity_filters = {
        'listener': and_filter([Listener]),
        'sfx': and_filter([SfxPlayer]),
        'sfx3d': and_filter([SfxPlayer, TerrainObject]),
        'music': and_filter([Music]),
    }

    def __init__(self):
        System.__init__(self)

        self.audio3d = Audio3DManager(base.sfxManagerList[0], None)
        #self.audio3d.set_distance_factor(1.0)
        #self.audio3d.set_drop_off_factor(0.0)

        # We need cross fading.
        base.musicManager.set_concurrent_sound_limit(2)

    def init_entity(self, filter, entity):
        if filter == 'listener':
            self.init_listener(entity)
        elif filter == 'sfx':
            self.init_sfx(entity)
        elif filter == 'music':
            self.init_music(entity)

    def init_listener(self, entity):
        if Camera in entity:
            root = entity[Camera]._root
        elif TerrainObject in entity:
            root = entity[TerrainObject]._root
        else:
            return

        listener = entity[Listener]
        listener._root = root
        listener._prev_pos = root.get_net_transform().get_pos()
        self.audio3d.attach_listener(root)

    def init_sfx(self, entity):
        player = entity[SfxPlayer]
        player._sfx = {}

        if TerrainObject in entity:
            root = entity[TerrainObject]._root
        else:
            root = None

        for sound in player.sounds:
            path = core.Filename('sfx', sound + '.ogg')
            sfx = self.audio3d.audio_manager.get_sound(path, positional=(root is not None))
            if player.loop:
                sfx.set_loop(True)
            player._sfx[sound] = sfx
            player._root = root

    def init_music(self, entity):
        music = entity[Music]
        music._songs = {}
        music._prev_songs = set()

        for song in music.songs:
            music._songs[song] = loader.load_music(core.Filename('music', song + '.ogg'))
            music._songs[song].set_loop(True)
            music._songs[song].set_volume(0)

    def play_sfx(self, entity, sound):
        player = entity[SfxPlayer]

        player._sfx[sound].set_volume(player.volume)
        player._sfx[sound].play()

        if player._root:
            pos = player._root.get_pos(self.audio3d.root)
            player._sfx[sound].set_3d_attributes(pos[0], pos[1], pos[2], 0, 0, 0)

        #print("Playing sound", sound)

    def change_music(self, entity, old_song, new_song):
        music = entity[Music]

        old = music._songs.get(old_song)
        if old:
            music._prev_songs.add(old)

        new = music._songs.get(new_song)
        if old and new:
            new.set_time(old.get_time())

        if new:
            new.play()
            music._active = new
            music._prev_songs.discard(new)

        print("Changing music to", new_song)

    def update(self, entities_by_filter):
        #for entity in entities_by_filter['listener']:
        #    listener = entity[Listener]
        #    pos = listener._root.get_net_transform().get_pos()
        #    vel = (pos - listener._prev_pos) / globalClock.dt
        #    self.audio3d.set_listener_velocity(vel)
        #    listener._prev_pos = pos

        for entity in entities_by_filter['sfx']:
            player = entity[SfxPlayer]
            for sound in player._queued:
                self.play_sfx(entity, sound)
            player._queued.clear()

        for entity in entities_by_filter['music']:
            music = entity[Music]

            # Fade in active song
            if music._active:
                volume = music._active.get_volume()
                if volume < 1.0:
                    volume = min(1.0, volume + globalClock.dt / MUSIC_FADE_TIME)
                    music._active.set_volume(volume)

            # Fade out inactive songs
            for song in tuple(music._prev_songs):
                volume = song.get_volume()
                if volume > 0.0:
                    volume = max(0.0, volume - globalClock.dt / MUSIC_FADE_TIME)
                    song.set_volume(volume)
                    if volume <= 0.0:
                        song.stop()
                        music._prev_songs.discard(song)

            if music._playing != music.current:
                self.change_music(entity, music._playing, music.current)
                music._playing = music.current

    def destroy_entity(self, filter, entity):
        pass
