import logging
import time

import azure.cognitiveservices.speech as speechsdk

from .appsettings import SPEECH_KEY, SPEECH_REGION

# See https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_sample.py#L325


# def speech_recognize_continuous_from_file(filepath):
#     """performs continuous speech recognition with input from an audio file"""
#     print("heloo from speech service")
#     print('filepath :' + filepath)
#     try:
#         print("heloo from speech service try") 
#         speech_config = speechsdk.SpeechConfig(
#             subscription=SPEECH_KEY, region=SPEECH_REGION)
#         speech_config.speech_recognition_language="en-US"
#         # audio_config = speechsdk.audio.AudioConfig(filename=filepath)
#         conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config)
#         speech_recognizer = speechsdk.SpeechRecognizer(
#             speech_config=speech_config, audio_config=audio_config)

#         done = False
#         texts = []

#         def stop_cb(evt: speechsdk.SessionEventArgs):
#             """callback that signals to stop continuous recognition upon receiving an event `evt`"""
#             # print('CLOSING on {}'.format(evt))
#             nonlocal done
#             done = True

#         def capture_text(evt: speechsdk.SessionEventArgs):
#             nonlocal texts
#             texts.append(evt.result.text)

#         print('texts: '+ texts[0])

#         # Connect callbacks to the events fired by the speech recognizer
#         # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
#         speech_recognizer.recognized.connect(capture_text)
#         # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
#         # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
#         # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
#         # stop continuous recognition on either session stopped or canceled events
#         speech_recognizer.session_stopped.connect(stop_cb)
#         speech_recognizer.canceled.connect(stop_cb)

#         # Start continuous speech recognition
#         speech_recognizer.start_continuous_recognition()
#         while not done:
#             time.sleep(.1)

#         speech_recognizer.stop_continuous_recognition()

#         return '\n'.join(texts)
#     except Exception as e:
#         print("heloo from speech service error") 
#         print(e) 
#         logging.info(e)
#         print("heloo from speech service error end") 
#         logging.error(e)
#         pass
#     return ''

def speech_recognize_continuous_from_file(filepath):
    try:
        """performs continuous speech recognition with input from an audio file"""
        # <SpeechContinuousRecognitionWithFile>
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        # speech_config.speech_recognition_language="en-US"
        audio_config = speechsdk.audio.AudioConfig(filename=filepath)

        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        done = False

        def stop_cb(evt):
            """callback that stops continuous recognition upon receiving an event `evt`"""
            print('CLOSING on {}'.format(evt))
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        all_results = []
        def handle_final_result(evt):
            all_results.append(evt.result.text)

        speech_recognizer.recognized.connect(handle_final_result)
        # Connect callbacks to the events fired by the speech recognizer
        speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
        speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
        speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
        # stop continuous recognition on either session stopped or canceled events
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # Start continuous speech recognition
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)

        return " ".join(all_results)
    except Exception as err:
        logging.info(err)
        print("Encountered exception. {}".format(err))
        return ""


# def speech_recognize_continuous_from_file(filepath):
#     try: 
#         print("heloo from speech service try")
#         print('filepath :' + filepath)
#         # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
#         speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
#         speech_config.speech_recognition_language="en-US"
#         audio_config = speechsdk.audio.AudioConfig(filename=filepath)
#         # audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
#         speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

#         print("Speak into your microphone.")
#         speech_recognition_result = speech_recognizer.recognize_once_async().get()
#         text = ""
#         if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             text = "{}".format(speech_recognition_result.text)
#             print("text recognized: " + text)
#             print("Recognized: {}".format(speech_recognition_result.text))
#         elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
#             print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
#         elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
#             cancellation_details = speech_recognition_result.cancellation_details
#             print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#             if cancellation_details.reason == speechsdk.CancellationReason.Error:
#                 print("Error details: {}".format(cancellation_details.error_details))
#                 print("Did you set the speech resource key and region values?")
#         return text
#     except Exception as err:
#         print("heloo from speech service error end") 
#         logging.info(err)
#         print("Encountered exception. {}".format(err))
#         return ""
    