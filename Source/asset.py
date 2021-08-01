from pygame import image, mixer


class audio_manager():
    def __init__(self, sounds):
        if sounds is not None:
            self.sounds = {}
            for i, s in enumerate(sounds):
                self.sounds[s] = (sounds[s], i)
            mixer.set_num_channels(len(self.sounds))

        else:
            self.sounds = None

    def play(self, name):

        assert name in self.sounds, f"{name} is an undefined sound"
        s = self.sounds[name]

        mixer.Channel(s[1]).play(s[0])


sound = audio_manager(None)

AMONGUS = image.load('data/sprites/textures/amongus.png')

JERMA = [
    image.load('data/sprites/textures/jerma4.png'),
    image.load('data/sprites/textures/jerma3.png'),
    image.load('data/sprites/textures/jerma2.png'),
    image.load('data/sprites/textures/jerma1.png'),
    image.load('data/sprites/textures/jerma2.png'),
    image.load('data/sprites/textures/jerma3.png'),
]
