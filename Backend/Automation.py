from AppOpener import close, open as appopen  # Import functions to open and close apps
from webbrowser import open as webopen  # Import web browser functionality
from pywhatkit import playonyt, search  # Import functions for Google search and YouTube playback
from dotenv import dotenv_values  # Import dotenv to manage env variables
from bs4 import BeautifulSoup  # Import BeautifulSoup for web scraping
from rich import print  # Import rich for styled console output
from groq import Groq  # Import Groq for AI Chat functionalities
import webbrowser  # Import webbrowser for opening URLs
import subprocess  # Import subprocess for interacting with system
import requests  # Import requests for making HTTP requests
import keyboard  # For keyboard-related functionalities
import asyncio  # For asynchronous programming
import os  # For operating system functionalities
import re  # For regular expressions to parse commands
import time  # For sleep operations
import tempfile  # For temporary file handling

# Load environment variables from .env file
env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env")  # Adjust path as needed

# Initialize Groq with api_key parameter
groq = Groq(api_key=env_vars['GroqAPIKey'])
client = groq  # Use the same instance

# Define CSS classes for parsing specific elements in HTML content
classes = [
    "Zcbuef", "hgKElc", "LKOoW XY7fec", "Z0LcW", "grtvk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "lzr6ld", "OQs4gc LfQK0", "V1z6cf",
    "webanswers-webanswers_table__webanswers-table", "doN0o ikb4Bb gsrt", "sXLa0e",
    "LWKFKe", "VQF4g", "qv3wpe", "kno-desc", "SPZz6b"
]

# Define a user-agent for parsing specific elements in the HTML content
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Common social media and website patterns for direct access
COMMON_WEBSITES = {
    "facebook": "https://www.facebook.com", "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com", "x": "https://www.twitter.com",
    "linkedin": "https://www.linkedin.com", "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com", "maps": "https://maps.google.com",
    "amazon": "https://www.amazon.com", "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com", "reddit": "https://www.reddit.com",
    "pinterest": "https://www.pinterest.com", "tiktok": "https://www.tiktok.com",
    "whatsapp": "https://web.whatsapp.com", "discord": "https://discord.com/app",
    "telegram": "https://web.telegram.org", "github": "https://github.com",
    "outlook": "https://outlook.live.com", "office": "https://www.office.com",
    "dropbox": "https://www.dropbox.com", "drive": "https://drive.google.com",
    "photos": "https://photos.google.com", "classroom": "https://classroom.google.com",
    "meet": "https://meet.google.com", "zoom": "https://zoom.us",
    "teams": "https://teams.microsoft.com",
}

# Command keywords that indicate specific actions
ACTION_KEYWORDS = {
    'open': ['open'],
    'close': ['close'],
    'play': ['play'],
    'search': ['google search', 'youtube search'],
    'system': ['system', 'volume up', 'volume down', 'mute', 'unmute'],
    'content': ['write', 'draft', 'letter', 'proposal', 'essay', 'report', 'content']
}

# Predefined professional responses for user interactions
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages
messages = []

# System message to provide context to the chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I'm {env_vars.get('Username', 'User')}, You're a versatile content writer. You can write any type of content including formal letters, business proposals, academic research papers, creative writing, blog posts, technical documentation, marketing copy, personal essays, speeches, and more. Your writing should be professional, well-structured, and tailored to the specific request. Adapt your tone, formatting, and vocabulary based on the type of content requested. For research papers, include citations and maintain academic rigor. For letters, follow appropriate formatting conventions. For creative content, showcase imagination while maintaining coherence."}]

# Function to perform Google search
async def GoogleSearch(Topic):
    """Perform Google search with improved reliability"""
    try:
        print(f"Searching Google for: {Topic}")
        # First try direct browser open with timeout
        try:
            search_query = Topic.replace(' ', '+')
            url = f"https://www.google.com/search?q={search_query}"
            print(f"Opening direct search URL: {url}")
            
            await asyncio.wait_for(
                asyncio.to_thread(webbrowser.open, url),
                timeout=5.0
            )
            return True
        except (asyncio.TimeoutError, Exception) as e:
            print(f"Direct Google search failed: {e}, trying alternative method")
            
        # If first method fails, try the pywhatkit method with timeout
        try:
            await asyncio.wait_for(
                asyncio.to_thread(search, Topic),
                timeout=8.0
            )
            return True
        except (asyncio.TimeoutError, Exception) as e2:
            print(f"Alternative Google search failed: {e2}")
            
            # Last resort - try DuckDuckGo
            try:
                ddg_url = f"https://lite.duckduckgo.com/lite/?q={Topic.replace(' ', '+')}"
                await asyncio.to_thread(webbrowser.open, ddg_url)
                print(f"Opened DuckDuckGo search as final fallback")
                return True
            except Exception as e3:
                print(f"All search attempts failed: {e3}")
                return False
    except Exception as e:
        print(f"Error in GoogleSearch: {e}")
        return False

# Function to generate content using AI and save it to a file
async def Content(Topic):
    try:
        print(f"Generating content for: {Topic}")

        # Nested function to open file in Notepad
        async def OpenNotepad(File):
            try:
                default_text_editor = 'notepad.exe'
                await asyncio.to_thread(subprocess.Popen, [default_text_editor, File])
                print(f"Opened {File} in Notepad")
                return True
            except Exception as e:
                print(f"Error opening Notepad: {e}")
                return False

        # Nested function to generate content using AI
        async def ContentWriterAI(prompt):
            messages.append({"role": "user", "content": f"{prompt}"})
            try:
                print("Generating content using AI...")
                completion = await asyncio.to_thread(client.chat.completions.create,
                    model="llama3-70b-8192",  # Updated model
                    messages=SystemChatBot + messages,
                    max_tokens=2048,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )
                Answer = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content
                Answer = Answer.replace("</s>", "")
                messages.append({"role": "assistant", "content": Answer})
                return Answer
            except Exception as e:
                print(f"Error in AI content generation: {e}")
                # Fallback to a different model if the first one fails
                try:
                    print("Attempting with fallback model...")
                    completion = await asyncio.to_thread(client.chat.completions.create,
                        model="mixtral-8x7b-32768",  # Fallback model
                        messages=SystemChatBot + messages,
                        max_tokens=2048,
                        temperature=0.7,
                        top_p=1,
                        stream=True,
                        stop=None
                    )
                    Answer = ""
                    for chunk in completion:
                        if chunk.choices[0].delta.content:
                            Answer += chunk.choices[0].delta.content
                    Answer = Answer.replace("</s>", "")
                    messages.append({"role": "assistant", "content": Answer})
                    return Answer
                except Exception as e2:
                    print(f"Fallback model also failed: {e2}")
                    return f"Error generating content: {e}"

        # Clean up topic
        if Topic.lower().startswith("content "):
            Topic = Topic[7:].strip()
        if not Topic:
            print("No valid topic provided")
            return False

        # Generate content
        print(f"Writing content for: {Topic}")
        ContentByAI = await ContentWriterAI(Topic)
        if not ContentByAI or "Error generating content" in ContentByAI:
            print("Failed to generate content")
            return False

        # Save to file
        try:
            safe_filename = re.sub(r'[\\/*?:"<>|]', "", Topic.lower().replace(' ', '_')[:30])
            data_dir = r"C:\Users\Dell\Downloads\AI\jarvis\Data"
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, f"{safe_filename}.txt")

            with open(file_path, "w", encoding='utf-8') as file:
                file.write(ContentByAI)
            print(f"Content saved to {file_path}")

            await OpenNotepad(file_path)
            return True
        except Exception as e:
            print(f"Error saving content: {e}")
            fd, temp_path = tempfile.mkstemp(suffix=".txt", text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as file:
                file.write(ContentByAI)
            print(f"Content saved to temporary file: {temp_path}")
            await OpenNotepad(temp_path)
            return True

    except Exception as e:
        print(f"Error in Content function: {e}")
        return False

# Function to search for a topic on YouTube
async def YouTubeSearch(Topic):
    try:
        print(f"Searching YouTube for: {Topic}")
        Url4Search = f"https://www.youtube.com/results?search_query={Topic.replace(' ', '+')}"
        await asyncio.to_thread(webbrowser.open, Url4Search)
        return True
    except Exception as e:
        print(f"Error in YouTube search: {e}")
        return False

# Function to play a video on YouTube
async def PlayYoutube(query):
    try:
        print(f"Playing on YouTube: {query}")
        search_query = query.replace(' ', '+')
        
        # Method 1: Direct approach with YouTube search and auto-click
        try:
            # Standard search URL with video filter to get videos first
            url = f"https://www.youtube.com/results?search_query={search_query}&sp=EgIQAQ%253D%253D"
            
            # Open Chrome with autoplay permissions
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--autoplay-policy=no-user-gesture-required", url], shell=True)
                print(f"Opened YouTube search in Chrome: {url}")
            else:
                # Fallback to default browser
                webbrowser.open(url)
                print(f"Opened YouTube search in default browser: {url}")
            
            # Wait for the page to load completely (crucial for reliable clicking)
            await asyncio.sleep(3.5)
            
            # After page is loaded, click on the first video
            try:
                import pyautogui
                
                # First try clicking directly where the first video should be
                # This position should work for standard 1080p+ screens
                screen_width, screen_height = pyautogui.size()
                # Click in the center of where the first thumbnail should be
                pyautogui.click(screen_width // 2, 250)
                print("Clicked on first video thumbnail position")
                
                # Wait a moment to ensure click is registered
                await asyncio.sleep(0.5)
                
                # Sometimes a single click doesn't work, so press Enter as well
                pyautogui.press('enter')
                print("Pressed Enter to ensure video plays")
                
                return True
            except Exception as click_err:
                print(f"Click error: {click_err}")
                
                # Try keyboard navigation as backup
                try:
                    # Tab to the first video (more tabs for reliable navigation)
                    pyautogui.press('tab', presses=6, interval=0.1)
                    pyautogui.press('enter')
                    print("Used keyboard navigation to play first video")
                    return True
                except Exception as key_err:
                    print(f"Keyboard navigation error: {key_err}")
            
            return True
            
        except Exception as e1:
            print(f"Method 1 failed: {e1}")
            
            # Method 2: Try pywhatkit's playonyt function
            try:
                print(f"Attempting playonyt with query: {query}")
                # Run with a longer timeout
                await asyncio.wait_for(
                    asyncio.to_thread(playonyt, query),
                    timeout=10.0
                )
                print("Successfully played video using playonyt")
                return True
            except Exception as e2:
                print(f"Method 2 failed: {e2}")
                
                # Method 3: Last resort - try YouTube Music for songs
                if any(term in query.lower() for term in ["song", "music", "listen", "track"]):
                    try:
                        music_url = f"https://music.youtube.com/search?q={search_query}"
                        webbrowser.open(music_url)
                        print(f"Opened YouTube Music as fallback: {music_url}")
                        
                        # Try to click on first result
                        await asyncio.sleep(3)
                        try:
                            import pyautogui
                            # Click near where first result should be
                            screen_width, screen_height = pyautogui.size()
                            pyautogui.click(screen_width // 2, 300)
                            pyautogui.press('enter')
                            print("Attempted to click first music result")
                        except Exception as music_err:
                            print(f"Music click error: {music_err}")
                            
                        return True
                    except Exception as e3:
                        print(f"Method 3 failed: {e3}")
                
                # Emergency fallback - at least open search results
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
                print("Opened YouTube search as emergency fallback")
                return True
    except Exception as e:
        print(f"Critical error in PlayYoutube: {e}")
        try:
            # Last resort emergency fallback
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            return True
        except:
            return False
# Update the OpenApp function with timeouts and better fallbacks

BRAVE_SHORTCUTS = {
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://twitter.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com"
}

async def OpenApp(app, sess=requests.session()):
    """Open an application or website with improved reliability"""
    if not app or app.strip() == "":
        print("Empty app name provided")
        return False
    
    app = app.strip().lower()
    print(f"Opening: {app}")
    
    # Step 1: Try as known website first (fastest)
    if app in COMMON_WEBSITES:
        try:
            await asyncio.wait_for(
                asyncio.to_thread(webbrowser.open, COMMON_WEBSITES[app]),
                timeout=5.0
            )
            print(f"Opened {app} as known website")
            return True
        except (asyncio.TimeoutError, Exception) as e:
            print(f"Known website opening failed: {e}")
    
    # Step 2: Try as desktop app with timeout
    try:
        await asyncio.wait_for(
            asyncio.to_thread(appopen, app, match_closest=True, output=True, throw_error=True),
            timeout=5.0  # 5 second timeout
        )
        print(f"Successfully opened {app} as desktop application")
        return True
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Desktop app opening failed or timed out: {e}")
    
    # Step 3: Try direct .com URL
    try:
        url = f"https://www.{app}.com"
        await asyncio.wait_for(
            asyncio.to_thread(webbrowser.open, url),
            timeout=5.0
        )
        print(f"Opened direct URL: {url}")
        return True
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Direct URL opening failed: {e}")
    
    # Step 4: Try direct .co.in URL for Indian sites
    try:
        url = f"https://www.{app}.co.in"
        await asyncio.wait_for(
            asyncio.to_thread(webbrowser.open, url),
            timeout=5.0
        )
        print(f"Opened direct Indian URL: {url}")
        return True
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Indian URL opening failed: {e}")
    
    # Step 5: Last resort - Google search with timeout
    try:
        search_url = f"https://www.google.com/search?q={app}"
        await asyncio.wait_for(
            asyncio.to_thread(webbrowser.open, search_url),
            timeout=5.0
        )
        print(f"Opened Google search for {app}")
        return True
    except Exception as e:
        print(f"Error in Google search fallback: {e}")
        return False

# Function to close an application
async def CloseApp(app):
    try:
        print(f"Closing: {app}")
        if "chrome" in app.lower():
            await asyncio.to_thread(subprocess.run, ['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, text=True)
            print("Chrome closed using taskkill")
            return True
        await asyncio.to_thread(close, app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"Error closing app: {e}")
        return False

# Function to execute system-level commands
async def System(command):
    try:
        print(f"Executing system command: {command}")
        command = command.lower()
        if command == "mute":
            await asyncio.to_thread(keyboard.press_and_release, "volume mute")
            return True
        elif command == "unmute":
            await asyncio.to_thread(keyboard.press_and_release, "volume unmute")
            return True
        elif command in ["volume up", "up", "volume_up", "volumeup"]:
            for _ in range(5):
                await asyncio.to_thread(keyboard.press_and_release, "volume up")
                await asyncio.sleep(0.1)
            return True
        elif command in ["volume down", "down", "volume_down", "volumedown"]:
            for _ in range(5):
                await asyncio.to_thread(keyboard.press_and_release, "volume down")
                await asyncio.sleep(0.1)
            return True
        else:
            print(f"Unknown system command: {command}")
            return False
    except Exception as e:
        print(f"Error in System command: {e}")
        return False

# Function to check if text starts with any action keyword
def starts_with_action_keyword(text):
    text = text.lower().strip()
    for action_type, keywords in ACTION_KEYWORDS.items():
        for keyword in keywords:
            if text.startswith(keyword + " ") or text == keyword:
                return True
    return False

# Function to detect if text is a content writing request
def is_content_request(text):
    for keyword in ACTION_KEYWORDS['content']:
        if keyword in text.lower():
            return True
    return False

# Function to detect if text is a command indicator
def is_command_indicator(text):
    text = text.lower().strip()
    # Check for command verbs
    indicators = ["open", "close", "play", "search", "google", "youtube", "volume", "system", "mute", "unmute"]
    for indicator in indicators:
        if text.startswith(indicator + " ") or text == indicator:
            return True
    return False

# Function to parse multiple commands from a single input string
def parse_commands(input_string):
    input_string = input_string.strip()
    if not input_string:
        return []
    
    # First split by command indicators like "then", "after that", etc.
    parts = re.split(r'\s+then\s+|\s+after\s+that\s+', input_string)
    
    all_commands = []
    
    for part in parts:
        # First check for "write" or "content" commands which might contain commas and "and"
        if is_content_request(part):
            # Check if there are command indicators within the content request
            subparts = []
            in_content = False
            content_request = ""
            
            # Split by commas first
            comma_parts = re.split(r'\s*,\s*', part)
            temp_parts = []
            
            for comma_part in comma_parts:
                # Then split by "and" if needed
                temp_parts.extend(re.split(r'\s+and\s+', comma_part))
            
            # Now process all split parts
            for subpart in temp_parts:
                subpart = subpart.strip()
                if not subpart:
                    continue
                
                # If this is a new command indicator, add any previous content request
                if is_command_indicator(subpart) and in_content:
                    all_commands.append(f"content {content_request.strip()}")
                    content_request = ""
                    in_content = False
                    subparts.append(subpart)
                # If this looks like a content request or we're already building one
                elif is_content_request(subpart) or in_content:
                    if not in_content:  # Starting a new content request
                        in_content = True
                        content_request = subpart
                    else:  # Adding to an existing content request
                        content_request += ", " + subpart
                else:  # Regular command
                    subparts.append(subpart)
            
            # Add any remaining content request
            if in_content and content_request:
                all_commands.append(f"content {content_request.strip()}")
            
            # Process any other commands found
            all_commands.extend(process_command_parts(subparts))
        else:
            # Handle regular commands (not content requests)
            comma_parts = re.split(r'\s*,\s*', part)
            temp_parts = []
            
            for comma_part in comma_parts:
                temp_parts.extend(re.split(r'\s+and\s+', comma_part))
                
            all_commands.extend(process_command_parts(temp_parts))
            
    return all_commands

# Add a new timeout helper function that can be used throughout the code

async def with_timeout(coroutine, timeout_seconds=10.0, fallback=None):
    """Execute a coroutine with a timeout and optional fallback"""
    try:
        return await asyncio.wait_for(coroutine, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        print(f"Operation timed out after {timeout_seconds} seconds")
        if fallback:
            try:
                if callable(fallback):
                    return await fallback()
                return fallback
            except Exception as e:
                print(f"Fallback failed: {e}")
        return False
    except Exception as e:
        print(f"Operation failed: {e}")
        if fallback:
            try:
                if callable(fallback):
                    return await fallback()
                return fallback
            except Exception as e:
                print(f"Fallback failed: {e}")
        return False

# Helper function to process individual command parts
def process_command_parts(parts):
    commands = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if is_content_request(part) and not part.lower().startswith("content "):
            commands.append(f"content {part}")
            continue
            
        processed = False
        for pattern, cmd_type in [
            (r'open\s+(\w+)', "open"),
            (r'close\s+(\w+)', "close"),
            (r'play\s+(.*?)(?=\s+(?:open|close|system|google|youtube)|$)', "play"),
            (r'google\s+search\s+(.*?)(?=\s+(?:open|close|play|system|youtube)|$)', "google search"),
            (r'youtube\s+search\s+(.*?)(?=\s+(?:open|close|play|system|google)|$)', "youtube search"),
            (r'(?:system\s+)?volume\s+up', "system volume up"),
            (r'(?:system\s+)?volume\s+down', "system volume down"),
            (r'(?:system\s+)?(?:volume\s+)?mute', "system mute"),
            (r'(?:system\s+)?(?:volume\s+)?unmute', "system unmute"),
        ]:
            match = re.search(pattern, part, re.IGNORECASE)
            if match:
                if cmd_type.startswith("system"):
                    commands.append(cmd_type)
                else:
                    commands.append(f"{cmd_type} {match.group(1).strip() if match.lastindex else ''}")
                processed = True
                break
                
        if not processed and part.strip():
            if "volume" in part.lower():
                if "up" in part.lower():
                    commands.append("system volume up")
                elif "down" in part.lower():
                    commands.append("system volume down")
                else:
                    commands.append(f"system {part}")
            elif is_content_request(part):
                commands.append(f"content {part}")
            else:
                commands.append(part)
                
    return commands

# Asynchronous function to translate and execute user commands
async def TranslateAndExecute(commands: list[str]):
    print(f"Translating and executing {len(commands)} commands")
    tasks = []
    cmd_descriptions = []

    for command in commands:
        command = command.strip()
        if not command:
            continue
        print(f"Processing command: {command}")

        if command.lower().startswith("open "):
            app_name = command.lower().removeprefix("open ").strip()
            if app_name and "open it" not in app_name and app_name != "file":
                tasks.append(OpenApp(app_name))
                cmd_descriptions.append(f"Opening {app_name}")

        elif command.lower().startswith("close "):
            app_name = command.lower().removeprefix("close ").strip()
            if app_name:
                tasks.append(CloseApp(app_name))
                cmd_descriptions.append(f"Closing {app_name}")

        elif command.lower().startswith("play "):
            query = command.removeprefix("play ").strip()
            if query:
                tasks.append(PlayYoutube(query))
                cmd_descriptions.append(f"Playing {query} on YouTube")

        elif command.lower().startswith("content "):
            topic = command.strip()
            tasks.append(Content(topic))
            cmd_descriptions.append(f"Generating content for {topic}")

        elif command.lower().startswith("google search "):
            query = command.removeprefix("google search ").strip()
            if query:
                tasks.append(GoogleSearch(query))
                cmd_descriptions.append(f"Google searching {query}")

        elif command.lower().startswith("youtube search "):
            query = command.removeprefix("youtube search ").strip()
            if query:
                tasks.append(YouTubeSearch(query))
                cmd_descriptions.append(f"YouTube searching {query}")

        elif command.lower().startswith("system "):
            cmd = command.removeprefix("system ").strip()
            if cmd:
                tasks.append(System(cmd))
                cmd_descriptions.append(f"Executing system command {cmd}")

        else:
            if any(keyword in command.lower() for keyword in ["write", "draft", "create", "letter", "essay", "report"]):
                tasks.append(Content(f"content {command}"))
                cmd_descriptions.append(f"Creating content for {command}")
            else:
                print(f"No function found for: {command}")
                cmd_descriptions.append(f"Unknown command: {command}")
                tasks.append(asyncio.sleep(0, result=False))  # Placeholder for unrecognized commands

    if not tasks:
        print("No valid commands to execute")
        return

    print(f"Executing {len(tasks)} commands: {', '.join(cmd_descriptions)}")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for desc, result in zip(cmd_descriptions, results):
        if isinstance(result, Exception):
            print(f"Command '{desc}' failed with error: {result}")
        else:
            success = "succeeded" if result else "failed"
            print(f"Command '{desc}' {success}")

# Add this function to handle closing all apps
async def CloseAllApps():
    """Closes all non-essential applications"""
    try:
        import psutil
        
        # List of essential processes we don't want to close
        essential = ['explorer.exe', 'svchost.exe', 'csrss.exe', 'winlogon.exe', 
                    'services.exe', 'lsass.exe', 'python.exe', 'pythonw.exe',
                    'chrome.exe', 'vscode.exe']  # Keep Chrome since we need it for speech recognition
        
        closed_apps = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # If it's a visible application with a window and not essential
                proc_name = proc.name().lower() 
                if proc_name.endswith('.exe') and proc_name not in essential:
                    try:
                        proc.terminate()
                        closed_apps.append(proc_name)
                        print(f"Closed {proc_name}")
                    except:
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if closed_apps:
            return f"Successfully closed the following applications: {', '.join(closed_apps)}"
        else:
            return "No applications needed to be closed."
    except Exception as e:
        print(f"Error closing all apps: {e}")
        return f"Error closing applications: {str(e)}"

# Then update the Automation function:
async def Automation(commands: list):
    """Process multiple automation commands"""
    try:
        results = []
        
        for command in commands:
            command = command.lower().strip()
            print(f"Processing command: {command}")
            
            # Special case for closing all apps
            if "close all" in command and ("app" in command or "application" in command):
                result = await CloseAllApps()
                results.append(result)
                continue
                
            # Handle standard open/close/play commands
            if command.startswith("open "):
                # Rest of your existing code for open
                pass
            elif command.startswith("close "):
                # Rest of your existing code for close
                pass
            # Rest of your existing function
        
        return "\n".join(results)
    except Exception as e:
        print(f"Error in Automation: {e}")
        return f"Error processing automation commands: {str(e)}"

# Test function to demonstrate usage
async def test_automation():
    print("Testing automation...")
    test_commands = [
        "open notepad",
        "system volume up",
        "content Write a short business letter introducing a new product",
        "play relaxing music",
        "google search Python tutorials"
    ]
    print(f"Executing test commands: {test_commands}")
    result = await Automation(test_commands)
    print(f"Test automation complete: {result}")

# Main execution
if __name__ == "__main__":
    print("PREPARING FOR INPUTS (JUST ONCE)")
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--test":
        asyncio.run(test_automation())
    else:
        print("Automation system ready. Enter 'exit' to quit.")
        print("You can enter multiple commands separated by 'and', commas, or in sequence.")
        print("Examples:")
        print("  - open facebook and play meditation music")
        print("  - open facebook, open instagram, play music")
        print("  - content Write a formal letter of resignation")
        print("  - write a comprehensive business proposal for a tech startup")
        print("  - open notepad, close calculator, system volume up")
        print("  - open chrome, play music, then write an essay, then close chrome")
        
        while True:
            try:
                user_input = input("\nEnter command: ")
                if user_input.lower() == 'exit':
                    break
                if not user_input.strip():
                    continue
                commands = parse_commands(user_input)
                print(f"Parsed {len(commands)} commands: {commands}")
                asyncio.run(Automation(commands))
            except KeyboardInterrupt:
                print("\nProgram interrupted")
                break
            except Exception as e:
                print(f"Error: {e}")