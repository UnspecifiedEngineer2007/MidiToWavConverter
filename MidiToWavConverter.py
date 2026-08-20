import os
import time
import sys
import numpy as np
Script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(Script_dir)
FluidSynthBinPath = r"C:\fluidsynth\bin"
os.add_dll_directory(FluidSynthBinPath)
os.environ["PATH"] = FluidSynthBinPath + os.path.pathsep + os.environ["PATH"]
import fluidsynth
import mido
import wave
FileInput = input("Input file name (except '.mid')")
SoundfontInput = input("Input Soundfont Name (except '.sf2')")
print("Currently known drum instrument number : General User GS :120, Fluid Soundfont : 128")
DrumInstrumentNumber = int(input("Please input your drum instrument number for prevent error"))
LoadSynth = fluidsynth.Synth(samplerate = 44100, gain=0.8)
SoundfontLoad = LoadSynth.sfload(f"./{SoundfontInput}.sf2")
for i in range(16):
    if i == 9:
        LoadSynth.program_select(i, SoundfontLoad, DrumInstrumentNumber, 0)
    else:
        LoadSynth.program_select(i, SoundfontLoad, 0, 0)
MidiFile = mido.MidiFile("./"+FileInput+".mid")
audio_data = []
for msg in MidiFile:
    if msg.time > 0:
        samples_to_render = int(44100*msg.time)
        if samples_to_render > 0:
            Sample = LoadSynth.get_samples(samples_to_render)
            audio_data.append(Sample)
    if msg.type == "note_on":
        LoadSynth.noteon(msg.channel, msg.note, msg.velocity)
    elif msg.type == "note_off":
        LoadSynth.noteoff(msg.channel, msg.note)
    elif msg.type == "program_change":
        if msg.channel == 9:
            LoadSynth.program_select(msg.channel, SoundfontLoad, DrumInstrumentNumber, msg.program)
        else:
            LoadSynth.program_select(msg.channel, SoundfontLoad, 0, msg.program)
    elif msg.type == "control_change":
        LoadSynth.cc(msg.channel, msg.control, msg.value)
audio_data.append(LoadSynth.get_samples(44100*2))
Flat_audio = np.concatenate(audio_data)
output_file = f"./{FileInput}.wav"
with wave.open(output_file, "wb") as wav_file:
    wav_file.setnchannels(2)
    wav_file.setsampwidth(2)
    wav_file.setframerate(44100)
    wav_file.writeframes(Flat_audio.astype(np.int16).tobytes())
LoadSynth.delete()
