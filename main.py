from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import pickle
from strsimpy.jaro_winkler import JaroWinkler
from collections import OrderedDict

import kivy
kivy.require('2.1.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Variables

questions = ['what', 'why', 'where', 'when', 'who', 'whom', 'whose', 'which']

data = []

# gTTS

def update_data(text):
    prefix = 'is are '
    text = prefix + text

    text = (int((1000 - len(text)) / 2) * '^ ') + text

    data.append(text)
    pickle.dump(data, open('data', 'wb'))
    speak('Data updated')

def speak(text):
    new_text = text

    new_text = new_text.replace('^ ', '')

    if 'my' in new_text:
        new_text = new_text.replace('my', 'your')
    elif 'your' in new_text:
        new_text = new_text.replace('your', 'my')
    
    new_text = new_text.replace('is is ', '')
    new_text = new_text.replace('is are ', '')

    print(new_text)

    tts = gTTS(text=new_text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    voice = AudioSegment.from_file(fp, format='mp3')
    play(voice)

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print('Exception: ' + str(e))
        
    return said

def analyze_text(text):
    print(text)

    # for i in range(len(questions)):
    #     if questions[i] in text:
    #         text_to_say = compare(text)
    #         speak(text_to_say)
    #         break
    #     elif (' is ' in text or ' are ' in text) and questions[i] not in text:
    #         update_data(text)
    #         break
    # else:
    #     speak('i don\'t know what you\'re saying')
    
    for q in questions:
        if q in text:
            speak(compare(text))
            break
    else:
        if ' is ' in text or ' are ' in text:
            update_data(text)
        else:
            speak('I don\'t know what you\'re saying')
    
def compare(text):
    diffs = {}

    jarowinkler = JaroWinkler()

    for i in range(len(data)):
        diff = jarowinkler.similarity(text, data[i])
        diffs[diff] = i
    
    sorted_diffs_keys = sorted(diffs.keys())
    sorted_diffs = {key:diffs[key] for key in sorted_diffs_keys}

    diffs = {}

    print(list(sorted_diffs.values()))

    index = list(sorted_diffs.values())[-1]
    
    return data[index]

# Startup

# data = pickle.load(open('data', 'rb'))

class MainScreen(GridLayout):
    def __init__(self) -> None:
        super().__init__()
        self.rows = 2
        self.cols = 1
        self.add_widget(Label(text='HEY, I AM BOT!\nClick the "Speak" button and start speaking.', halign='center', font_size='24px'))
        
        self.speak_btn = Button(text='Speak', font_size='24px')
        self.speak_btn.bind(on_press=self.pressed)
        self.add_widget(self.speak_btn)
    
    def pressed(self, instance):
        analyze_text(get_audio())

class MyApp(App):

    def build(self):
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
