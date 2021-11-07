import deepspeech
import os
import numpy as np
import pyaudio
import time

cwd = os.getcwd()

model_file_path = os.path.join(cwd, 'starfleetlogger/models/deepspeech-0.9.3-models.pbmm')
model = deepspeech.Model(model_file_path)

scorer_file_path = os.path.join(cwd, 'starfleetlogger/models/deepspeech-0.9.3-models.scorer')
model.enableExternalScorer(scorer_file_path)

lm_alpha = 0.75
lm_beta = 1.85
model.setScorerAlphaBeta(lm_alpha, lm_beta)

beam_width = 500
model.setBeamWidth(beam_width)

# import wave
# filename = os.path.join(cwd, 'starfleetlogger/audio/8455-210777-0068.wav')
# w = wave.open(filename, 'r')
# rate = w.getframerate()
# frames = w.getnframes()
# buffer = w.readframes(frames)
# print(rate, model.sampleRate, len(buffer))

# ds_stream = model.createStream()

# buffer_len = len(buffer)
# offset = 0
# batch_size = 16384
# text = ''

# while offset < buffer_len:
#     end_offset = offset + batch_size
#     chunk = buffer[]
ds_stream = model.createStream()

text_so_far = ''
def process_audio(in_data, frame_count, time_info, status):
    global text_so_far
    data16 = np.frombuffer(in_data, dtype=np.int16)
    ds_stream.feedAudioContent(data16)
    text = ds_stream.intermediateDecode()
    if text != text_so_far:
        print('Interim text = {}'.format(text))
        text_so_far = text
    return (in_data, pyaudio.paContinue)

audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024,
    stream_callback=process_audio
)

print('Please start speaking, when done press Ctrl-C...')
stream.start_stream()

try:
    while stream.is_active():
        time.sleep(0.1)
except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print('Finished recording.')
    
    text = ds_stream.finishStream()
    print('Final text = {}'.format(text))

print('Hello there')