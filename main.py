from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,)
from Backend.Model import FirstLayerDMM
from Backend.RealTimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.Automation import Content, GoogleSearch, Automation
from Backend.ImageGeneration import generate_and_open_images
from dotenv import dotenv_values
from asyncio import run, create_task, gather, wait_for
from time import sleep
import subprocess
import threading
import json
import os
import asyncio
import time

# Global cache for reading ChatLog.json
_chatlog_cache = None

env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} = Welcome {Username}, I am doing great! How can I help you today?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "image generation ", "chatbot", "automation", "real time search engine", "text to speech", "speech to text", "image to text", "text to image"]

# Add this to the beginning of main.py
data_dir = os.path.join(os.path.dirname(__file__), "Data")
os.makedirs(data_dir, exist_ok=True)

# Ensure ChatLog.json exists
chatlog_path = os.path.join(data_dir, "ChatLog.json")
if not os.path.exists(chatlog_path):
    with open(chatlog_path, "w", encoding='utf-8') as f:
        f.write("[]")

def ShowDefaultChatIfNoChats():
    File = open(os.path.join(os.path.dirname(__file__), "Data", "ChatLog.json"), 'r', encoding='utf-8')    
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(DefaultMessage)
            
def ReadChatLogJson():
    with open(os.path.join(os.path.dirname(__file__), "Data", "ChatLog.json"), 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
            
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    
    with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))
        
def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split("\n")
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8')
        File.write(result)
        File.close()
        
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    
    # Reset the session state when application starts
    try:
        from Backend.Chatbot import reset_session
        reset_session()
        print("Session reset - Jarvis will introduce itself on first interaction only")
    except Exception as e:
        print(f"Error resetting session: {e}")
    
InitialExecution()

# Helper function to detect image generation requests
def is_image_request(query):
    """Check if the query is requesting image generation"""
    image_keywords = ["generate image", "create image", "make image", "draw", "picture of", 
                      "photo of", "image of", "generate a picture", "design", "generate an image"]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in image_keywords)

# Helper function to extract image prompt
def extract_image_prompt(query):
    """Extract the image description from a query"""
    query_lower = query.lower()
    
    # Remove common prefixes
    for prefix in ["generate image of", "generate image", "create image of", "create image", 
                   "make an image of", "make an image", "draw a", "generate a picture of", 
                   "make a picture of", "i want an image of", "can you generate an image of"]:
        if prefix in query_lower:
            return query_lower.replace(prefix, "").strip()
    
    # If no specific pattern, use the whole query removing "image" words
    cleaned = query_lower
    for word in ["image", "generate", "create", "picture", "photo", "draw"]:
        cleaned = cleaned.replace(word, "").strip()
    
    if len(cleaned) > 5:
        return cleaned
    
    # Fallback to whole query
    return query

# Async wrapper for generate_and_open_images with timeout
async def generate_image_with_timeout(prompt, timeout=25.0):
    """Generate image with timeout to prevent hanging"""
    try:
        return await wait_for(
            asyncio.to_thread(generate_and_open_images, prompt), 
            timeout=timeout
        )
    except asyncio.TimeoutError:
        print(f"Image generation timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"Error generating image: {e}")
        return False

def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ContentExecution = False
        SearchExecution = False
        
        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()
        
        # Check for exit commands
        if Query and any(word in Query.lower() for word in ["exit", "bye", "goodbye", "quit", "stop"]):
            Answer = "Goodbye! It was nice talking to you."
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Shutting down...")
            TextToSpeech(Answer)
            SetMicrophoneStatus("False")  # Turn off microphone only on exit
            return False
        
        # Add debug information
        print(f"Recognized query: '{Query}'")
        
        if not Query or Query.strip() == "":
            SetAssistantStatus("I didn't catch that...")
            sleep(2)
            SetAssistantStatus("Available...")
            return False
            
        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Processing...")
        
        # Pre-process multi-task requests into separate commands
        if "and" in Query.lower() and any(keyword in Query.lower() for keyword in 
                                          ["play", "search", "open", "close", "get", "stock", "price", "generate", "image"]):
            print(f"Pre-processed multi-task request into: [{Query.lower()}]")
            # We're keeping the original query but will do specialized parsing

        # IMPROVED APPROACH: First check for direct image requests before using the model
        direct_image_request = is_image_request(Query)
        if direct_image_request:
            print("Detected direct image request, bypassing model for faster response")
            Decisions = ["generate image " + extract_image_prompt(Query)]
        else:
            # Get decisions from the model
            Decisions = FirstLayerDMM(Query)
            
            # Direct command detection for better reliability
            if "play" in Query.lower() and not any("play" in d.lower() for d in Decisions):
                parts = Query.lower().split("play", 1)
                if len(parts) > 1 and parts[1].strip():
                    print("Adding missing play command based on query")
                    Decisions.append(f"play {parts[1].strip()}")
                    
            # Direct stock price detection
            if ("stock" in Query.lower() or "price of" in Query.lower()) and not any("realtime" in d.lower() for d in Decisions):
                print("Adding missing stock price search based on query")
                Decisions.append(f"realtime {Query}")
                
            # Direct search detection
            if any(term in Query.lower() for term in ["search for", "look up", "find"]) and not any(("search" in d.lower() or "realtime" in d.lower()) for d in Decisions):
                search_query = Query.lower()
                for term in ["search for", "look up", "find"]:
                    if term in search_query:
                        search_query = search_query.split(term, 1)[1].strip()
                        break
                if search_query:
                    print(f"Adding missing search command based on query: {search_query}")
                    Decisions.append(f"google search {search_query}")
        
        print(f"Decision from model: {Decisions}")
        
        if not Decisions or len(Decisions) == 0:
            Answer = "I'm sorry, I couldn't process your request. Please try again."
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Error processing request")
            TextToSpeech(Answer)
            return False
        
        # IMPROVED DECISION PARSING - handle multiple types and parse commands better
        decision_types = []
        automation_commands = []
        content_requests = []
        search_requests = []
        image_requests = []
        general_requests = []
        
        # First check original query for image keywords - this improves reliability
        if is_image_request(Query) and not any(d.startswith(("image", "generate image")) for d in Decisions):
            print("Forcing image detection based on original query")
            decision_types.append("image")
            image_requests.append("image " + extract_image_prompt(Query))
        
        # Check for direct YouTube/play command in the original query
        if "play" in Query.lower() and not any(d.startswith("play") for d in Decisions):
            print("Detected direct play command in query")
            play_content = Query.lower().split("play", 1)[1].strip()
            if play_content:
                decision_types.append("automation")
                automation_commands.append(f"play {play_content}")
        
        for decision in Decisions:
            decision = decision.lower().strip()
            
            # Check for specific task types
            if decision.startswith("general"):
                decision_types.append("general")
                general_requests.append(decision)
            elif decision.startswith("realtime"):
                decision_types.append("realtime")
                search_requests.append(decision)
            elif decision.startswith("google search"):
                decision_types.append("google_search")
                search_requests.append(decision)
            elif decision.startswith("image") or decision.startswith("generate image"):
                decision_types.append("image")
                image_requests.append(decision)
            elif decision.startswith(("open", "close", "play")):
                decision_types.append("automation")
                automation_commands.append(decision)
            elif decision.startswith("system"):
                decision_types.append("automation")
                automation_commands.append(decision)
            elif decision.startswith("content"):
                decision_types.append("content")
                content_requests.append(decision)
            elif "search" in decision:
                # Generic search request - assume google
                decision_types.append("google_search")
                search_requests.append(f"google search {decision}")
        
        print(f"Decision types: {decision_types}")
        print(f"Automation commands: {automation_commands}")
        print(f"Content requests: {content_requests}")
        print(f"Search requests: {search_requests}")
        print(f"Image requests: {image_requests}")
        
        # Prepare a combined answer for multiple tasks
        combined_answers = []
        total_tasks = len(automation_commands) + len(content_requests) + len(search_requests) + len(image_requests)
        
        # HANDLE AUTOMATION
        if "automation" in decision_types and automation_commands:
            try:
                SetAssistantStatus("Performing tasks...")
                
                # Special handling for YouTube play commands
                youtube_play_commands = [cmd for cmd in automation_commands if cmd.startswith("play")]
                other_commands = [cmd for cmd in automation_commands if not cmd.startswith("play")]
                
                # Process YouTube commands with special attention
                if youtube_play_commands:
                    for yt_cmd in youtube_play_commands:
                        yt_query = yt_cmd.replace("play", "").strip()
                        SetAssistantStatus(f"Playing {yt_query} on YouTube...")
                        
                        # Import the YouTube function properly
                        from Backend.Automation import PlayYoutube
                        
                        try: 
                            # Run the YouTube function directly with debug message
                            sucess = asyncio.run(asyncio.wait_for(PlayYoutube(yt_query), timeout = 5.0))
                            if success:
                                combined_answers.append(f"I'm playing {yt_query} on YouTube.")
                            else:
                                combined_answers.append(f"I had trouble playing {yt_query} on YouTube, but I've opened the search results.")
                        except asyncio.TimeoutError:
                            print("YouTube playback timeout - continuing with search results")
                            combined_answers.append(f"I'm searching for {yt_query} on YouTube.")
                        except Exception as yt_e:
                            print(f"YouTube error: {yt_e}")
                            combined_answers.append(f"I had trouble playing {yt_query}, but I've opened YouTube.")
                        # Try up to 2 times for YouTube playback
                        success = False
                        for attempt in range(2):
                            try:
                                success = asyncio.run(PlayYoutube(yt_query))
                                if success:
                                    print(f"Successfully played YouTube on attempt {attempt+1}")
                                    break
                                time.sleep(1)  # Small delay between attempts
                            except Exception as yt_e:
                                print(f"YouTube attempt {attempt+1} failed: {yt_e}")
                                time.sleep(1)  # Brief pause before retry
                        

                # Process other automation commands normally
                if other_commands:
                    result = asyncio.run(Automation(other_commands))
                    part_answer = f"I've executed the following tasks: {', '.join(other_commands)}"
                    combined_answers.append(part_answer)
                
                TaskExecution = True
            except Exception as e:
                print(f"Error in automation: {e}")
                part_answer = f"I couldn't complete all the automation tasks. Error: {e}"
                combined_answers.append(part_answer)
        
        # HANDLE CONTENT GENERATION
        if "content" in decision_types and content_requests:
            try:
                for content_req in content_requests:
                    SetAssistantStatus("Generating content...")
                    content_query = content_req.replace("content", "").strip()
                    asyncio.run(Content(content_query))
                    part_answer = f"I've created content for: {content_query}"
                    combined_answers.append(part_answer)
                    ContentExecution = True
            except Exception as e:
                print(f"Error in content generation: {e}")
                part_answer = f"I couldn't complete all the content generation tasks. Error: {e}"
                combined_answers.append(part_answer)
        
        # HANDLE SEARCH REQUESTS
        if ("realtime" in decision_types or "google_search" in decision_types) and search_requests:
            try:
                for search_req in search_requests:
                    if search_req.startswith("realtime"):
                        SetAssistantStatus("Getting real-time information...")
                        search_query = search_req.replace("realtime", "").strip()
                        if not search_query:
                            search_query = Query
                            
                        # Special handling for stock price queries
                        if any(term in search_query.lower() for term in ["stock", "price", "share", "market"]):
                            # Extract company name for stock query
                            company_name = None
                            company_keywords = ["apple", "microsoft", "google", "amazon", "tesla", "facebook", "meta"]
                            for company in company_keywords:
                                if company in search_query.lower():
                                    company_name = company
                                    break
                            
                            # If we found a company name, use it directly
                            if company_name:
                                SetAssistantStatus(f"Getting stock price for {company_name}...")
                                try:
                                    # Import directly from RealTimeSearchEngine
                                    from Backend.RealTimeSearchEngine import get_stock_price
                                    stock_result = get_stock_price(company_name)
                                    if stock_result:
                                        combined_answers.append(stock_result)
                                        continue
                                except Exception as stock_e:
                                    print(f"Error getting stock price: {stock_e}")
                        
                        # Regular realtime search
                        search_result = RealtimeSearchEngine(QueryModifier(search_query))
                        part_answer = f"{search_result}"
                        combined_answers.append(part_answer)
                    elif search_req.startswith("google search"):
                        SetAssistantStatus("Searching Google...")
                        search_query = search_req.replace("google search", "").strip()
                        if not search_query:
                            search_query = Query
                        asyncio.run(GoogleSearch(search_query))
                        part_answer = f"I've searched Google for: {search_query}"
                        combined_answers.append(part_answer)
                    SearchExecution = True
            except Exception as e:
                print(f"Error in search: {e}")
                part_answer = f"I couldn't complete all the search tasks. Error: {e}"
                combined_answers.append(part_answer)
        
        # HANDLE IMAGE GENERATION - FIXED VERSION WITH PROPER INDENTATION
        if "image" in decision_types and image_requests:
            try:
                for image_req in image_requests:
                    SetAssistantStatus("Generating image...")
                    # Better image prompt extraction
                    image_query = extract_image_prompt(image_req)
                    
                    # If image query is empty or too short, use the original query
                    if not image_query or len(image_query) < 5:
                        image_query = extract_image_prompt(Query)
                    
                    print(f"Generating image with prompt: {image_query}")
                    
                    # Run the image generation directly with proper error handling
                    try:
                        # Call the function directly with debug message
                        print(f"DEBUG: About to call generate_and_open_images with: {image_query}")
                        result = generate_and_open_images(image_query)
                        print(f"DEBUG: Image generation result: {result}")
                        
                        if result:
                            part_answer = f"I've generated images based on: {image_query}"
                        else:
                            part_answer = f"I attempted to generate images for '{image_query}' but encountered an issue."
                        
                        combined_answers.append(part_answer)
                        ImageExecution = True
                    
                    except Exception as e:
                        print(f"Error in image generation: {e}")
                        part_answer = f"I couldn't generate the requested image. Error: {e}"
                        combined_answers.append(part_answer)
            except Exception as e:
                print(f"Error in image generation section: {e}")
                part_answer = f"I couldn't generate the requested image. Error: {e}"
                combined_answers.append(part_answer)
        
        # GENERAL QUERY HANDLING (CHATBOT) if no other tasks were executed
        if ("general" in decision_types or not any([TaskExecution, ContentExecution, SearchExecution, ImageExecution])):
            try:
                SetAssistantStatus("Thinking...")
                if general_requests:
                    for general_req in general_requests:
                        query_text = general_req.replace("general", "").strip()
                        if not query_text:
                            query_text = Query
                        Answer = ChatBot(QueryModifier(query_text))
                        combined_answers.append(Answer)
                else:
                    # If no tasks were executed or recognized, treat as general query
                    Answer = ChatBot(QueryModifier(Query))
                    combined_answers.append(Answer)
            except Exception as e:
                print(f"Error in chatbot: {e}")
                part_answer = f"I couldn't process your question. Error: {e}"
                combined_answers.append(part_answer)
        
        # Combine all answers into one response
        final_answer = " ".join(combined_answers)
        
        # Limit answer length if too long for faster TTS
        if len(final_answer) > 300:
            final_answer = final_answer[:297] + "..."
            
        ShowTextToScreen(f"{Assistantname}: {final_answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(final_answer)
        
        return True
        
    except Exception as e:
        print(f"Error in MainExecution: {e}")
        Answer = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Error occurred")
        TextToSpeech(Answer)
        return True  # Keep mic on even after errors
    
def FirstThread():
    while True:
        try:
            currentStatus = GetMicrophoneStatus()
            
            if currentStatus == "True":
                print("Starting main execution")
                
                # Execute main function but keep mic on unless explicitly exited
                result = MainExecution()
                
                # Only turn off mic if user explicitly said exit/bye
                if result is False and "Shutting down" in GetAssistantStatus():
                    print("User requested exit, turning mic off")
                    SetMicrophoneStatus("False")
                else:
                    # Keep mic on for continuous conversation
                    print("Keeping microphone ON for next command")
                    # Ensure the mic stays on
                    SetMicrophoneStatus("True")
                
                # Reset status to available
                SetAssistantStatus("Available...")
            else:
                AIStatus = GetAssistantStatus()
                if "Available..." not in AIStatus and AIStatus.strip() != "":
                    print(f"Current AI status: {AIStatus}")
                if "Available..." in AIStatus:
                    sleep(0.1)
                else: 
                    SetAssistantStatus("Available...")
            
            # Reduce CPU usage
            sleep(0.1)
                
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            SetAssistantStatus("Error occurred, please try again")
            sleep(2)
    
def SecondThread():
    GraphicalUserInterface()
    
if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()