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
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

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
    
InitialExecution()

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
        
        # Get decisions from the model
        Decisions = FirstLayerDMM(Query)
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
        
        # Prepare a combined answer for multiple tasks
        combined_answers = []
        total_tasks = len(automation_commands) + len(content_requests) + len(search_requests) + len(image_requests)
        
        # HANDLE AUTOMATION
        if "automation" in decision_types and automation_commands:
            try:
                SetAssistantStatus("Performing tasks...")
                result = run(Automation(automation_commands))
                part_answer = f"I've executed the following tasks: {', '.join(automation_commands)}"
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
                    run(Content(content_query))
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
                        SetAssistantStatus("Searching...")
                        search_query = search_req.replace("realtime", "").strip()
                        if not search_query:
                            search_query = Query
                        search_result = RealtimeSearchEngine(QueryModifier(search_query))
                        part_answer = f"Search result: {search_result[:100]}..."
                        combined_answers.append(part_answer)
                    elif search_req.startswith("google search"):
                        SetAssistantStatus("Searching Google...")
                        search_query = search_req.replace("google search", "").strip()
                        if not search_query:
                            search_query = Query
                        run(GoogleSearch(search_query))
                        part_answer = f"I've searched Google for: {search_query}"
                        combined_answers.append(part_answer)
                    SearchExecution = True
            except Exception as e:
                print(f"Error in search: {e}")
                part_answer = f"I couldn't complete all the search tasks. Error: {e}"
                combined_answers.append(part_answer)
        
        # HANDLE IMAGE GENERATION
        if "image" in decision_types and image_requests:
            try:
                for image_req in image_requests:
                    SetAssistantStatus("Generating image...")
                    image_query = image_req.replace("image", "").replace("generate", "").strip()
                    generate_and_open_images(image_query)
                    part_answer = f"I've generated an image based on: {image_query}"
                    combined_answers.append(part_answer)
                    ImageExecution = True
            except Exception as e:
                print(f"Error in image generation: {e}")
                part_answer = f"I couldn't generate the requested image. Error: {e}"
                combined_answers.append(part_answer)
        
        # GENERAL QUERY HANDLING (CHATBOT) if no other tasks were executed
        if "general" in decision_types and not any([TaskExecution, ContentExecution, SearchExecution, ImageExecution]):
            try:
                SetAssistantStatus("Thinking...")
                for general_req in general_requests:
                    query_text = general_req.replace("general", "").strip()
                    if not query_text:
                        query_text = Query
                    Answer = ChatBot(QueryModifier(query_text))
                    combined_answers.append(Answer)
            except Exception as e:
                print(f"Error in chatbot: {e}")
                part_answer = f"I couldn't process your question. Error: {e}"
                combined_answers.append(part_answer)
        
        # If no tasks or only failed tasks, handle as general query
        if not combined_answers:
            SetAssistantStatus("Thinking...")
            Answer = ChatBot(QueryModifier(Query))
            combined_answers.append(Answer)
        
        # Combine all answers into one response
        final_answer = " ".join(combined_answers)
        
        # Limit answer length if too long
        if len(final_answer) > 500:
            final_answer = final_answer[:497] + "..."
            
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
            
    