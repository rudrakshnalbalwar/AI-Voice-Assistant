import pygame 
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# load environment variables
env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env")

AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")
print(f"Using voice: {AssistantVoice}")

# Ensure Data directory exists
data_dir = r"C:\Users\Dell\Downloads\AI\jarvis\Data"
os.makedirs(data_dir, exist_ok=True)

# Aynschronous function to convert text to speech
async def TextToAudioFile(text) -> None:
    file_path = r"C:\Users\Dell\Downloads\AI\jarvis\Data\speech.mp3"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # Create the communicate object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)
    print(f"Audio file created at {file_path}")
    
# Function to manage Text-to-speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            print(f"Processing: {Text[:50]}..." if len(Text) > 50 else f"Processing: {Text}")
            
            # Convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))
            
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()
            
            # Load the generated speech file into pygame mixer
            pygame.mixer.music.load(r"C:\Users\Dell\Downloads\AI\jarvis\Data\speech.mp3")
            pygame.mixer.music.play()
            print("Playing audio...")
            
            # Loop until the audio is done playing or the function stops
            # FIXED: Changed pygame.time.clock() to pygame.time.Clock() (uppercase C)
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                clock.tick(10)
                
            return True
        except Exception as e:
            print(f"Error in TTS: {e}")
            return False  # Added return False to exit the loop on error
            
        finally:
            try:
                # Call the provided function with false to signal the end of tts
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                
            except Exception as e:
                print(f"Error in TTS Finally: {e}")    
                
# Function to manage Text-to-speech (TTS) functionality with additional responses for long test
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    # List of provided responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    # If the text is very long (more than 4 sentences and 250 characters), add a rseponse message
    if len(Data) > 4 or len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
        
    # Otherwise just play the whole text
    else:
        TTS(Text, func)
        
# Function to test audio
def test_audio():
    print("\nTesting audio playback...")
    TTS("This is a test of the text to speech system. If you can hear this message, audio is working correctly.")
    print("Audio test complete")
        
# Main function 
if __name__ == "__main__":
    print("Text-to-Speech Program")
    print("Type 'test' to check if audio is working")
    print("Type 'exit' to quit")
    
    try:
        while True:
            user_input = input("\nEnter the text: ")
            
            if user_input.lower() == "exit":
                print("Exiting...")
                break
                
            if user_input.lower() == "test":
                test_audio()
                continue
                
            if user_input.strip():
                TextToSpeech(user_input)
            else:
                print("Please enter some text")
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.mixer.quit()
        print("Program ended")