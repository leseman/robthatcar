import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.music_volume = 0.5  # Default music volume
        self.sfx_volume = 0.5

    def load_sound(self, name, file_path):
        sound = pygame.mixer.Sound(file_path)
        self.sounds[name] = sound

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def stop_sound(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def load_music(self, file_path):
        pygame.mixer.music.load(file_path)

    def play_music(self, loops=-1):
        pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def fade_out_music(self, time):
        pygame.mixer.music.fadeout(time)

sounds = SoundManager()
sounds.load_music("sounds/ambient.ogg")

sound_files = {
    "pain": "sounds/pain.wav",
    "dead": "sounds/dead.wav"
}

for sound_name, file_path in sound_files.items():
    sounds.load_sound(sound_name, file_path)