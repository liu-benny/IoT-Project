import simpleaudio as sa

direct = "/home/benny/Desktop/IoT-Project/phase-4/multipage-dash-app-main/sounds/"

filename1 = direct + 'sound1.wav'
wave_obj1 = sa.WaveObject.from_wave_file(filename1)
filename2 = direct + 'sound2.wav'
wave_obj2 = sa.WaveObject.from_wave_file(filename2)
filename3 = direct + 'fan1.wav'
wave_obj3 = sa.WaveObject.from_wave_file(filename3)
filename4 = direct + 'fan2.wav'
wave_obj4 = sa.WaveObject.from_wave_file(filename4)

def lightOff():
    play_obj = wave_obj1.play()


def lightOn():
    play_obj = wave_obj2.play()
    
def fan():
    play_obj = wave_obj3.play()


def fan2():
    play_obj = wave_obj4.play()

    
    