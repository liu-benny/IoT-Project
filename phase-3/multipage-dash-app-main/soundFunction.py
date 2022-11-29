import simpleaudio as sa

filename1 = 'sound1.wav'
wave_obj1 = sa.WaveObject.from_wave_file(filename1)
filename2 = 'sound2.wav'
wave_obj2 = sa.WaveObject.from_wave_file(filename2)
filename3 = 'fan1.wav'
wave_obj3 = sa.WaveObject.from_wave_file(filename3)
filename4 = 'fan2.wav'
wave_obj4 = sa.WaveObject.from_wave_file(filename4)

def lightOff():
    play_obj = wave_obj1.play()


def lightOn():
    play_obj = wave_obj2.play()
    
def fan():
    play_obj = wave_obj3.play()


def fan2():
    play_obj = wave_obj4.play()

    
    