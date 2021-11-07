from threading import Thread
from queue import Queue
import speech_recognition as sr
from Log import LOG

r = sr.Recognizer()
audio_queue = Queue()

log_status = LOG.NOTBEGUN

def recognize_worker():
    # this runs in a background thread
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None: break  # stop processing if the main thread is done

        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # use google api to recognize speech
            speech = r.recognize_google(audio)
            
            global log_in_progress
            
            # check if the hotwords are in the sentence to begin log
            temp_speech = speech.lower()
            if 'captain' in temp_speech and 'log' in temp_speech and 'star' in temp_speech and 'date' in temp_speech:
                print('start the log')
                log_status = LOG.INPROGRESS # set the logging process

            print(log_in_progress)

            if 'captain' in temp_speech and 'out' in temp_speech and len(temp_speech.split()) <= 7:
                print('end the log')
                log_status = LOG.OVER

            print("Google Speech Recognition thinks you said " + speech)
        except sr.UnknownValueError:
            print("Recognition software could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Recognition software; {0}".format(e))

        audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()
with sr.Microphone() as source:
    try:
        while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop