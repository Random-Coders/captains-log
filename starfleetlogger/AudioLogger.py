from queue import Queue
from threading import Thread

import speech_recognition as sr


class AudioLogger(object):
    def __init__(self):
        self.r = sr.Recognizer()
        self.audio_queue = Queue()
        self.record = ""

    def recognize_worker(self):
        # this runs in a background thread
        while True:
            audio = (
                self.audio_queue.get()
            )  # retrieve the next audio processing job from the main thread
            if audio is None:
                break  # stop processing if the main thread is done

            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                print(
                    "Google Speech Recognition thinks you said "
                    + self.r.recognize_google(audio)
                )
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(
                        e
                    )
                )

            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue

    def record(self):
        # start a new thread to recognize audio, while this thread focuses on listening
        recognize_thread = Thread(target=self.recognize_worker)
        recognize_thread.daemon = True
        recognize_thread.start()
        with sr.Microphone() as source:
            try:
                while (
                    True
                ):  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
                    self.audio_queue.put(self.r.listen(source))
            except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
                pass

        self.audio_queue.join()  # block until all current audio processing jobs are done
        self.audio_queue.put(None)  # tell the recognize_thread to stop
        recognize_thread.join()  # wait for the recognize_thread to actually stop
