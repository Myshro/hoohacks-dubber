import os
# import tempfile
# from gtts import gTTS
# import requests, json
# import io
import wave
import pyaudio
from pyt2s.services import stream_elements
from moviepy.audio.io.AudioFileClip import AudioFileClip
# import time
# import pyttsx3

class Dubber:
    def __init__(self, default_output_device_index=20):
        self.default_output_device_index = default_output_device_index
        self.available_speakers = {
            "russel": "Takumi",  # Default mapping
            "takumi": "Takumi"
            # Add more speaker mappings as needed
        }
    
    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        devices = []
        
        print("Available Audio Output Devices:")
        print("------------------------------")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:  # Only list output devices
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxOutputChannels']
                })
                print(f"Device {i}: {info['name']} (Channels: {info['maxOutputChannels']})")
        
        p.terminate()
        return devices
    
    def dub(self, text, speaker="russel", output_device_index=None):
        """
        Generate speech from text and play it through the specified output device.
        
        Args:
            text (str): Text to convert to speech
            speaker (str): Speaker voice to use (mapped to actual TTS voice)
            output_device_index (int, optional): Audio output device index
        
        Returns:
            bool: Success status of the dubbing operation
        """
        if not text or len(text.strip()) == 0:
            print("Warning: Empty text provided for dubbing")
            return False
            
        # Use default output device if none specified
        if output_device_index is None:
            output_device_index = self.default_output_device_index
            
        # Map speaker name to actual TTS service voice name
        tts_voice = self.available_speakers.get(speaker.lower(), self.available_speakers["russel"])
        
        try:
            # Generate speech using pyt2s (stream_elements service)
            mp3_data = stream_elements.requestTTS(text, tts_voice)
            
            # Save the returned MP3 data to a temporary file
            mp3_filename = 'temp_speech.mp3'
            with open(mp3_filename, 'wb') as f:
                f.write(mp3_data)
            
            # Convert the MP3 file to WAV format using MoviePy
            wav_filename = 'temp_speech.wav'
            audio_clip = AudioFileClip(mp3_filename)
            audio_clip.write_audiofile(wav_filename, codec='pcm_s16le', logger=None)
            
            # Open the generated WAV file and play it
            with wave.open(wav_filename, 'rb') as f:
                p = pyaudio.PyAudio()
                
                def _callback(in_data, frame_count, time_info, status):
                    data = f.readframes(frame_count)
                    return (data, pyaudio.paContinue)
                
                stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                                channels=f.getnchannels(),
                                rate=f.getframerate(),
                                output=True,
                                output_device_index=output_device_index,
                                stream_callback=_callback)
                
                stream.start_stream()
                while stream.is_active():
                    pass
                
                stream.stop_stream()
                stream.close()
                p.terminate()
            
            # Clean up the temporary files
            os.remove(mp3_filename)
            os.remove(wav_filename)
            return True
            
        except Exception as e:
            print(f"Error in dubbing process: {str(e)}")
            return False
    
    def set_default_output_device(self, device_index):
        """
        Set the default output device for dubbing.
        
        Args:
            device_index (int): Audio output device index to use by default
        """
        self.default_output_device_index = device_index
        return True
    

def main():
    # vv = Voicevox()
    # vv.speak(text='英単語を')
    dubber = Dubber()
    dubber.dub('血気')


if __name__ == "__main__":
    main()