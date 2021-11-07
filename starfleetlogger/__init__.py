from math import log
from threading import Thread
from queue import Queue
import speech_recognition as sr
from starfleetlogger.LogEnum import LOG
import encrypt


r = sr.Recognizer()
audio_queue = Queue()
key = encrypt.load_key()

log_status = LOG.NOTBEGUN
stardate = ''
audio_data = []

def recognize_worker():
    # this runs in a background thread
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None: break  # stop processing if the main thread is done

        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # use google api to recognize speech
            speech = r.recognize_google(audio)
            
            global log_status
            global stardate
            global audio_data

            # check if the hotwords are in the sentence to begin the log
            temp_speech = speech.lower()
            if 'captain' in temp_speech and 'log' in temp_speech and 'star' in temp_speech and 'date' in temp_speech:
                print('start the log')
                log_status = LOG.INPROGRESS # set the logging process
                date_idx = temp_speech.find('date') + 5 
                stardate = speech[date_idx:]
                stardate = stardate.replace(' ', '-', -1)

            if log_status == LOG.INPROGRESS:
                audio_data.append(audio.get_flac_data())

            # check if the hotwords are in the sentence to end the log
            if 'captain' in temp_speech and 'out' in temp_speech and len(temp_speech.split()) <= 5:
                print('end the log')
                log_status = LOG.OVER

            print(log_status)

            print("Google Speech Recognition thinks you said " + speech)
        except sr.UnknownValueError:
            print("Recognition software could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Recognition software; {0}".format(e))
        except sr.WaitTimeoutError:
            print("Listening for too long and no phrase started")
        except:
            pass

        audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()
with sr.Microphone() as source:
    try:
        while log_status != LOG.OVER:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source, phrase_time_limit=7))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass


# # Code for encryption
# with sr.Microphone() as source:
#     audio = r.listen(source)
for audio_snippet in audio_data:
    print('1')
    encrypt.encrypt(f"Stardate-{stardate}.encrypted", key, audio_snippet) # begin the encyrption and storing process

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop