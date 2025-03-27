from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time
import re
import string

# Create Data directory if it doesn't exist
os.makedirs(r"C:\Users\Dell\Downloads\AI\jarvis\Data", exist_ok=True)

# Load environment variables from the .env file
env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env") 

# Define the HTML code with improved multilingual speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Speech Recognition</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
        button { margin: 10px; padding: 10px 20px; }
        #output { min-height: 100px; border: 1px solid #ccc; padding: 10px; margin-top: 20px; text-align: left; overflow-y: auto; max-height: 300px; }
        .recording { color: red; }
        .language-selector { margin: 10px 0; }
        #detected-language { margin-top: 5px; font-style: italic; }
        #status-info { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <h1 id="status">Voice Recognition</h1>
    <div class="language-selector">
        <label for="language-select">Select language:</label>
        <select id="language-select">
            <option value="auto">Auto-detect</option>
            <option value="en-US">English (US)</option>
            <option value="hi-IN">Hindi</option>
            <option value="en-IN">English (India)</option>
        </select>
    </div>
    <div id="detected-language">Detected language: -</div>
    <div id="status-info">Waiting 5 seconds after speech stops before processing</div>
    <button id="start">Start Recognition</button>
    <button id="end">Stop Recognition</button>
    <div id="output"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const startButton = document.getElementById('start');
            const endButton = document.getElementById('end');
            const output = document.getElementById('output');
            const status = document.getElementById('status');
            const statusInfo = document.getElementById('status-info');
            const languageSelect = document.getElementById('language-select');
            const detectedLanguage = document.getElementById('detected-language');
            
            let recognition;
            let finalTranscript = '';
            let lastSpeechTime = Date.now();
            let silenceTimer = null;
            const silenceLimit = 5000; // 5 seconds of silence to trigger completion
            
            startButton.addEventListener('click', startRecognition);
            endButton.addEventListener('click', stopRecognition);
            
            // Auto-start recognition when page loads
            setTimeout(startRecognition, 1000);

            function startRecognition() {
                if (recognition) {
                    recognition.stop();
                }
                
                finalTranscript = '';
                status.textContent = 'Listening...';
                status.className = 'recording';
                
                // Get selected language or use auto-detect
                const selectedLanguage = languageSelect.value;
                
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = selectedLanguage;
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.maxAlternatives = 3;  // Get multiple possibilities

                recognition.onresult = function(event) {
                    let interimTranscript = '';
                    
                    // Reset silence timer whenever we get results
                    lastSpeechTime = Date.now();
                    clearTimeout(silenceTimer);
                    
                    // If available, show the detected language
                    if (event.results[0] && event.results[0].isFinal) {
                        // Can't directly access language detection in all browsers, but we can log it
                        console.log("Speech detected, possible language: " + selectedLanguage);
                        detectedLanguage.textContent = "Active language: " + selectedLanguage;
                    }
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        // Get the most confident result
                        const transcript = event.results[i][0].transcript;
                        const confidence = event.results[i][0].confidence;
                        
                        // Log confidence for debugging
                        console.log(`Confidence: ${confidence.toFixed(2)}, Text: ${transcript}`);
                        
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript + ' ';
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    
                    output.textContent = finalTranscript + interimTranscript;
                    output.scrollTop = output.scrollHeight; // Auto-scroll to bottom
                    
                    // Update status to show user that we're waiting for silence
                    statusInfo.textContent = "Waiting 5 seconds after speech stops before processing...";
                    
                    // Start silence detection timer
                    silenceTimer = setTimeout(function() {
                        if (Date.now() - lastSpeechTime > silenceLimit) {
                            console.log("Silence detected - considering speech complete");
                            status.textContent = 'Processing...';
                            status.className = '';
                            if (finalTranscript.trim() !== '' || output.textContent.trim() !== '') {
                                // Only stop if we actually have some text
                                stopRecognition();
                            } else {
                                // If nothing was said, keep listening
                                clearTimeout(silenceTimer);
                            }
                        }
                    }, silenceLimit);
                };

                recognition.onend = function() {
                    // If recognition ends but we're still recording, restart it
                    if (status.className === 'recording' && finalTranscript.trim() === '') {
                        console.log('Recognition ended prematurely, restarting...');
                        recognition.start();
                    }
                };
                
                recognition.onerror = function(event) {
                    console.log('Recognition error: ' + event.error);
                    
                    // If we get no-speech error and using auto-detect, try Hindi specifically
                    if (event.error === 'no-speech' && selectedLanguage === 'auto') {
                        console.log('Switching to Hindi recognition...');
                        recognition.stop();
                        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                        recognition.lang = 'hi-IN';
                        languageSelect.value = 'hi-IN';
                        detectedLanguage.textContent = "Switched to: Hindi";
                        recognition.continuous = true;
                        recognition.interimResults = true;
                        recognition.start();
                        return;
                    }
                    
                    // Restart on error, except for no-speech which just means silence
                    if (event.error !== 'no-speech' && status.className === 'recording') {
                        setTimeout(function() {
                            recognition.start();
                        }, 500);
                    }
                };
                
                try {
                    recognition.start();
                    console.log('Recognition started with language: ' + selectedLanguage);
                } catch (e) {
                    console.error('Error starting recognition: ' + e);
                }
            }

            function stopRecognition() {
                if (recognition) {
                    recognition.stop();
                    status.textContent = 'Completed';
                    status.className = '';
                    console.log('Recognition stopped');
                    // Make sure we get either finalTranscript or the current output
                    if (!finalTranscript && output.textContent) {
                        finalTranscript = output.textContent;
                    }
                }
            }
            
            // Function to get the full transcript - called by selenium
            window.getFullTranscript = function() {
                stopRecognition();
                return finalTranscript || output.textContent || '';
            };
            
            // Allow changing language during session
            languageSelect.addEventListener('change', function() {
                if (status.className === 'recording') {
                    // Restart recognition with new language
                    stopRecognition();
                    setTimeout(startRecognition, 500);
                }
            });
        });
    </script>
</body>
</html>'''

# Write the HTML code to a file
html_path = r"C:\Users\Dell\Downloads\AI\jarvis\Data\Voice.html"
with open(html_path, "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# Set Chrome options for the webdriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--log-level=3")  # Suppress Chrome logs
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--silent")
# Using headless mode for production
chrome_options.add_argument("--headless=new")

# Initialize the chrome webdriver using the ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\..\Frontend\Files"
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file
def SetAssistantStatus(status):
    with open(f"{TempDirPath}/Status.data", "w", encoding='utf-8') as file:
        file.write(status)
        
# Function to identify likely language from text
def detect_language(text):
    # Basic heuristic language detection
    text = text.lower()
    
    # Hindi character detection (Devanagari Unicode range)
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    
    # Character sets that suggest languages
    english_chars = sum(1 for c in text if c in string.ascii_letters)
    
    # Words characteristic of Hindi written in Latin script (Hinglish)
    hinglish_words = ["hai", "kya", "aap", "main", "hum", "tum", "kaise", "kyun", 
                      "kyon", "acha", "theek", "nahi", "nahin", "mein", "ho", "ke", 
                      "ki", "ka", "se", "ko", "bhai", "yaar", "accha", "karo", "mere"]
    
    hinglish_count = sum(1 for word in text.split() if word in hinglish_words)
    
    # Calculate proportions relative to text length
    text_len = max(1, len(text))
    hindi_ratio = hindi_chars / text_len
    english_ratio = english_chars / text_len
    hinglish_ratio = hinglish_count / max(1, len(text.split()))
    
    # Make decision based on proportions
    if hindi_ratio > 0.1:  # If text contains some Devanagari
        return "hi"
    elif hinglish_ratio > 0.15:  # If many Hinglish words
        return "hi"
    elif english_ratio > 0.5:  # If mostly English characters
        return "en"
    else:
        # If we can't determine confidently, try both
        return "auto"

# Function to modify a query to ensure proper punctuation and formatting
def QueryModifier(Query):
    if not Query:
        return ""
    
    new_query = Query.strip()
    if len(new_query) == 0:
        return ""
    
    # Make first letter uppercase
    new_query = new_query[0].upper() + new_query[1:]
    
    # Add proper punctuation at the end if missing
    if new_query[-1] not in [".", "?", "!"]:
        # Check if query is a question
        question_words = ["what", "where", "when", "why", "how", "who", "which", "whose", "whom", "can", "could", "would", "should", "do", "does", "did", "is", "are", "was", "were"]
        first_word = new_query.lower().split()[0] if new_query.split() else ""
        
        if first_word in question_words:
            new_query += "?"
        else:
            new_query += "."
    
    return new_query

# Enhanced translation function with better language detection
def TranslateText(Text):
    try:
        print(f"Attempting to process text: {Text}")
        
        # Clean up the text
        Text = Text.strip()
        
        # Fix common speech recognition errors
        # This looks for patterns in misrecognized speech rather than specific fixed phrases
        corrections = [
            (r"\bokay so\b", "kaise ho"),
            (r"\bhow many\b", "kaise"),
            (r"\bhow many (bhai|by|bye)\b", "kaise ho bhai"),
            (r"\bcase so\b", "kaise ho"),
            (r"\bcancer\b", "kaise"),
            (r"\bkidnap\b", "kya"),
            (r"\bgrandpa\b", "kya")
        ]
        
        # Apply pattern-based corrections
        for pattern, replacement in corrections:
            Text = re.sub(pattern, replacement, Text, flags=re.IGNORECASE)
        
        # Detect the likely language
        detected_lang = detect_language(Text)
        print(f"Detected language: {detected_lang}")
        
        # If non-English content detected, translate
        if detected_lang == "hi":
            print("Hindi content detected, translating...")
            # Try with explicit Hindi source
            try:
                translation = mt.translate(Text, "en", "hi")
                print(f"Hindi translation result: {translation}")
                return translation
            except Exception as e:
                print(f"Hindi translation failed: {e}, trying auto...")
                # Fallback to auto
                translation = mt.translate(Text, "en", "auto")
                print(f"Auto translation result: {translation}")
                return translation
        else:
            # First check if text is already mostly English
            english_word_count = sum(1 for word in Text.lower().split() 
                              if word in ["i", "am", "is", "are", "the", "a", "an", "and", "or", "but", 
                                         "how", "what", "when", "where", "why", "who", "which", 
                                         "hello", "hi", "hey", "good", "thanks", "thank", "you"])
            
            # If more than 40% of words are common English words, assume it's already English
            if english_word_count / max(1, len(Text.split())) > 0.4:
                print("Text appears to be mostly English, skipping translation")
                return Text
                
            # Otherwise translate with auto-detection
            translation = mt.translate(Text, "en", "auto")
            print(f"Auto translation result: {translation}")
            return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return Text  # Return original text if translation fails

# Function to perform speech recognition using the Chrome webdriver
def SpeechRecognition(timeout=90):  # Increased timeout for longer inputs
    try:
        # Avoid using global driver - create new one each time
        chrome_options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--use-fake-device-for-media-stream")
        chrome_options.add_argument("--log-level=3")  # Suppress Chrome logs
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--headless=new")
        
        # Create a new driver instance for each recognition
        service = Service(ChromeDriverManager().install())
        local_driver = webdriver.Chrome(service=service, options=chrome_options)
        # Open the HTML file in the browser
        absolute_path = "file:///" + os.path.abspath(html_path).replace("\\", "/")
        print(f"Opening: {absolute_path}")
        driver.get(absolute_path)
        
        # Wait for the page to load
        time.sleep(2)
        
        # Check if we should use Hindi mode based on previous results
        try:
            # You could store the last detected language in a file
            lang_path = os.path.join(r"C:\Users\Dell\Downloads\AI\jarvis\Data", "last_language.txt")
            if os.path.exists(lang_path):
                with open(lang_path, "r") as f:
                    last_lang = f.read().strip()
                    if last_lang == "hi":
                        # Set the dropdown to Hindi
                        driver.execute_script("document.getElementById('language-select').value='hi-IN'; const event = new Event('change'); document.getElementById('language-select').dispatchEvent(event);")
                        print("Set recognition language to Hindi based on previous detection")
        except Exception as e:
            print(f"Error setting language: {e}")
        
        # Wait for recognition to start (auto-starts in our HTML)
        print("Waiting for speech recognition to begin...")
        SetAssistantStatus("Listening...")
        
        # Initial wait time
        max_wait = timeout  # Maximum seconds to wait for speech
        start_time = time.time()
        last_text = ""
        
        while time.time() - start_time < max_wait:
            try:
                # Get the recognized text from the HTML output element
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.ID, "output"))
                )
                Text = element.text.strip()
                
                status_element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.ID, "status"))
                )
                status_text = status_element.text.strip()
                
                # If we have text and the status is "Completed", the speech is done
                if Text and status_text == "Completed":
                    print(f"Speech completed. Recognized text ({len(Text.split())} words): {Text[:100]}...")
                    
                    # Always process with best language detection
                    SetAssistantStatus("Processing...")
                    translated_text = TranslateText(Text)
                    
                    # Save the detected language for next time
                    try:
                        detected_lang = detect_language(Text)
                        with open(os.path.join(r"C:\Users\Dell\Downloads\AI\jarvis\Data", "last_language.txt"), "w") as f:
                            f.write(detected_lang)
                    except Exception as e:
                        print(f"Error saving language detection: {e}")
                        
                    return QueryModifier(translated_text)
                
                # Display interim text for debugging
                if Text and Text != last_text:
                    if len(Text) > 100:
                        print(f"Interim text ({len(Text.split())} words): {Text[:100]}...")
                    else:
                        print(f"Interim text ({len(Text.split())} words): {Text}...")
                    last_text = Text
                
                # Check if enough time has passed with stable text (5+ seconds)
                # This handles cases where the recognition doesn't properly finish
                if Text and time.time() - start_time > 20 and Text == last_text:
                    # Force completion after a long stable period
                    try:
                        print("Text stable for a while, getting final transcript...")
                        final_text = driver.execute_script("return window.getFullTranscript();")
                        if final_text:
                            SetAssistantStatus("Processing...")
                            translated_text = TranslateText(final_text)
                            return QueryModifier(translated_text)
                    except Exception as e:
                        print(f"Error getting transcript: {e}")
                
            except TimeoutException:
                pass  # Keep waiting
            
            time.sleep(0.5)  # Short pause between checks
        try:
            local_driver.quit()
        except:
            pass
        
        # If we reach here, we've timed out. Try to get any text we have
        print("Speech recognition timeout reached")
        
        try:
            # Force getting the final transcript
            final_text = driver.execute_script("return window.getFullTranscript();")
            if final_text:
                print(f"Got text before timeout: {final_text[:100]}...")
                SetAssistantStatus("Processing...")
                translated_text = TranslateText(final_text)
                return QueryModifier(translated_text)
        except Exception as e:
            print(f"Error getting final transcript: {e}")
            
        SetAssistantStatus("No speech detected")
        return QueryModifier(translated_text)


    except Exception as e:
        print(f"Speech recognition error: {e}")
        SetAssistantStatus("Error in speech recognition")
        return ""

# Main Program - only runs if this file is executed directly
if __name__ == "__main__":
    print("Enhanced Multilingual Speech Recognition System Started")
    print("The system will listen until you pause for 5 seconds")
    print("Supports English and Hindi (including Hinglish)")
    print("Say 'exit', 'bye', or 'band karo' to quit the program")
    try:
        while True:
            Text = SpeechRecognition(timeout=120)  # 2 minutes maximum per input
            if Text:
                word_count = len(Text.split())
                print(f"Final result ({word_count} words): {Text[:100]}...")
                if word_count > 100:
                    print("(Text truncated for display. Full text captured for processing.)")
                
                # Check if user wants to exit in multiple languages
                if any(exit_phrase in Text.lower() for exit_phrase in [
                    "stop listening", "exit", "quit", "bye", "goodbye", "terminate",
                    "band karo", "rukna", "bas", "bandh karo", "khatam"  # Hindi exit commands
                ]):
                    print("Exit command detected. Shutting down...")
                    break
                
                # Add your code to process the text or send it to another system
                
                print("\nListening for next input...")
            else:
                print("\nNo input detected. Listening again...")
    except KeyboardInterrupt:
        print("\nExiting speech recognition system")
    finally:
        # Clean up resources
        driver.quit()
        print("Browser closed")