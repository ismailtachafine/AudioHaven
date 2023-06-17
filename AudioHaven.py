import PySimpleGUI as sg
import pyttsx3
import speech_recognition as sr
from pygame import mixer
from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ntpath
import pathlib

engine = pyttsx3.init()
r = sr.Recognizer()
mixer.init()
sg.theme("DarkTeal2")
paused = False
list = []


col1 = [
    [sg.Text("")],
    [sg.Text("Select an audio file to add to the playlist ( WAV or MP3 ):", pad = (40,0)), sg.In(), sg.FileBrowse(key="-BR3-", file_types=(("WAV File", "*.wav"),("MP3 File", "*.mp3"))), sg.Button("Add", key = '-ADD-')],
    [sg.Text("")],
    [sg.Text("Choose the audio to play from the playlist:", pad = (40,0))],
    [sg.Text("")],
    [sg.Listbox(values = list, size=(100,15), key='-LISTBOX-', enable_events=True, text_color='black', select_mode='simple', pad = (40,0))],
    [sg.Text("")],
    [sg.Button("Play", key = '-PLAY-', target='-BR3-', pad = (100,0)), sg.Button("Pause/Resume", key = '-PAUSE-', pad = (100,0)), sg.Button("Stop", key = '-STOP-', pad = (100,0))]
]

col2 = [
    [sg.Text("Volume", pad=(210,0))],
    [sg.Slider(range=(0,100), default_value=50, orientation='v', key='-SLIDER-', pad=(200,0))]
]

col3 = [
    [sg.Text("Choose the audio file to sample : ", pad = (20,10)), sg.Input(pad = (30,0)), sg.FileBrowse(key="-BR4-", file_types=(("WAV File", "*.wav"),))],
    [sg.Text("Enter the extremities of the sample : ", pad = (20,24)), sg.Text("Ext 1: ", pad = (20,0)), sg.Input(key="-IN2-", size=(10,0)), sg.Text("Ext 2: ", pad = (20,0)), sg.Input(key="-IN3-", size=(10,0)), sg.Button("Submit", key = '-SUB4-', target='-BR4-', pad = (28,0))],
    [sg.Text("")],
    [sg.Button("Plot Audio", key='-PLOTX-', pad=(300,0))],
    [sg.Canvas(size = (640,460), key = '-CANVAS1-', background_color='black')]
]

col4 = [
    [sg.Text('Output :', pad = (20,0)), sg.Output(size = (70,6), key = '-OUTPUT2-', pad=(0,3))],
    [sg.Text("")],
    [sg.Button("Plot Sample", key='-PLOTY-', pad=(300,0))],
    [sg.Canvas(size = (640,460), key = '-CANVAS2-', background_color='black')]
]

tab1 = [
    [sg.Text("1 . Play Audio :", font = 'Franklin 20', pad = (0,20), justification='center', expand_x=True)],
    [sg.Column(col1), sg.Column(col2)]
]

tab2 = [
    [sg.Text("2 . From Text to Speech :", font = 'Franklin 20', pad = (0,20), justification='center', expand_x=True)],
    [sg.Text("")],
    [sg.Text("Gender of speaker : ", pad = (40,0)), sg.Combo(['Male', 'Female'], default_value='Male', key='-CHOICE-', pad = (80,0))],
    [sg.Text("")],
    [sg.Text("Choose the text file to read : ", pad = (40,0)), sg.Input(pad = (30,0)), sg.FileBrowse(key="-BR1-", file_types=(("Text Document", "*.txt"),)), sg.Button("Read", key = '-SUB1-', target='-BR1-')],
    [sg.Text("")],
    [sg.Text("Or just type the text to read : ", pad = (40,0)), sg.Multiline(key="-IN1-", pad = (25,0), size = (100,15)), sg.Button("Read", key = '-SUB2-', pad = (20,0))]
]
    
tab3 = [
    [sg.Text("3 . From Speech to Text :", font = 'Franklin 20', pad = (0,20), justification='center', expand_x=True)],
    [sg.Text("")],
    [sg.Text("Choose the audio file to transcript (WAV): ", pad = (40,0)), sg.Input(pad = (30,0)), sg.FileBrowse(key="-BR2-", file_types=(("WAV File", "*.wav"),)), sg.Button("Transcript", key = '-SUB3-')],
    [sg.Text("")],
    [sg.Text("The transcription might take a few seconds, please wait until completion.", pad = (40,0))],
    [sg.Text("")],
    [sg.Text('Output :', pad = (40,0)), sg.Output(size = (100,15), key = '-OUTPUT1-')]
]

tab4 = [
    [sg.Text("4 . Audio Manipulation :", font = 'Franklin 20', pad = (0,20), justification='center', expand_x=True)],
    [sg.Column(col3, key='-COL3-'), sg.Column(col4)]
    

]

layout = [
    [sg.Text("WELCOME TO AUDIOHAVEN!", font = 'Franklin 30', justification= 'center', expand_x= True, pad = (0,20))],
    [sg.TabGroup([[sg.Tab('Play Audio', tab1), sg.Tab('From Text to Speech', tab2), sg.Tab('From Speech to Text', tab3), sg.Tab('Audio Manipulation', tab4)]], tab_location='centertop', expand_x=True, expand_y=True, pad=(50,25))]
]

def draw_figure(a, canvas):
    figure = plt.figure()
    plt.plot(a)
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def read_audio(name, N1, N2):
    global x, y, row
    row = []
    (fs,x) = read(name)
    y = x[int(N1) : int(N2)]
    a = np.min(y)
    b = np.max(y)
    row.append(f'Table of Audio : {x}')
    row.append(f'Size of table : {x.size}')
    row.append(f'Table of Sample : {y}')
    row.append(f'Min value of the sample : {a}')
    row.append(f'Max value of the sample: {b}')

def text_to_speech(text):
    speaker = values['-CHOICE-']
    if speaker == 'Male':
        engine.say(text)
        engine.runAndWait()
    if speaker == 'Female':
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.setProperty("voice", voices[0].id)
    
def path_leaf(path):
    head, tail = ntpath.split(path)
    return head, tail or ntpath.basename(head)

def play(a):
    global paused
    paused = False
    b = '\\'.join([list[list.index(a)-1],a]) + list[list.index(a)+1]
    mixer.music.load(b)
    mixer.music.play(loops=0)


window = sg.Window('AudioHaven', layout, finalize=True).Finalize()
window.Maximize()
    
while True:

    event, values = window.read(timeout=10)
    mixer.music.set_volume(values['-SLIDER-']/100)

    if event == sg.WIN_CLOSED:
        break

    elif event == '-SUB1-':
        try:
            fichier = open(values['-BR1-'] , 'r')
            text = fichier.read()
            text_to_speech(text)
        except:
            pass

    elif event == '-SUB2-':
        try:
            text = values['-IN1-']
            text_to_speech(text)
        except:
            pass

    elif event == '-SUB3-':
        try:
            audio = values['-BR2-']
            with sr.AudioFile(audio) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                window['-OUTPUT1-'].update(text)
        except:
            pass

    elif event == '-ADD-':
        list.append(path_leaf(values['-BR3-'])[0])
        if '.wav' in path_leaf(values['-BR3-'])[1]:
            list.append(path_leaf(values['-BR3-'])[1].replace('.wav',''))
        if '.mp3' in path_leaf(values['-BR3-'])[1]:
            list.append(path_leaf(values['-BR3-'])[1].replace('.mp3',''))
        list.append(pathlib.Path(path_leaf(values['-BR3-'])[1]).suffix)
        window['-LISTBOX-'].update(values = list[1::3])

    elif event == '-PLAY-':
        try:
            play(values['-LISTBOX-'][0])
            
        except:
            pass

    elif event == '-PAUSE-':
        try:
            if paused == False:
                mixer.music.pause()
                paused = True
            else:
                mixer.music.unpause()
                paused = False
        except:
            pass

    elif event == '-STOP-':
        try:
            mixer.music.stop()
        except:
            pass
        
    elif event == '-SUB4-':
        try:
            read_audio(values['-BR4-'], values['-IN2-'], values['-IN3-'])
            window['-OUTPUT2-'].update(("\n").join(row))
        except:
            pass

    elif event == '-PLOTX-':
        try:
            draw_figure(x, window['-CANVAS1-'].TKCanvas)
        except:
            pass

    elif event == '-PLOTY-':
        try:
            draw_figure(y, window['-CANVAS2-'].TKCanvas)
        except:
            pass
 