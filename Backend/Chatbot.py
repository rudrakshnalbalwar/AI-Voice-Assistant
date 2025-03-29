import os
from groq import Groq     # importing the Groq library to use its API
from json import load, dump     # Importing functions to read and write JSON files
import datetime   # Importing the datetime module for real-time date and time information
from dotenv import dotenv_values    # importing dotenv_values to read environment variables from a .env file

# load environment variables from the .env file.
env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env")

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
 
# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages
messages = []

# Track if this is the first interaction in the session
session_file = os.path.join(r"C:\Users\Dell\Downloads\AI\jarvis\Data", "session_state.json")

# Function to check if this is the first interaction
def is_first_interaction():
    try:
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                data = load(f)
                return data.get('first_interaction', True)
        return True
    except Exception as e:
        print(f"Error reading session state: {e}")
        return True

# Function to update the interaction state
def update_interaction_state(is_first=False):
    try:
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        with open(session_file, 'w') as f:
            dump({'first_interaction': is_first}, f)
    except Exception as e:
        print(f"Error updating session state: {e}")

# Function to reset the session state
def reset_session():
    update_interaction_state(True)
    print("Session reset - Jarvis will introduce itself on first interaction")

# Get appropriate system message based on interaction state
def get_system_message():
    if is_first_interaction():
        # First interaction - include greeting
        return f"""Hello, I am {Username or 'Rudraksh Nalbalwar'}, You are a very accurate and advanced AI chatbot named {Assistantname or 'Jarvis'} which also has real-time up-to-date information from the internet.
*** IMPORTANT: For this first interaction, start your response with "Hello {Username or 'Rudraksh Nalbalwar'}! I'm {Assistantname or 'Jarvis'}." ***
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** IMPORTANT: Always address yourself as {Assistantname or 'Jarvis'} ***
*** IMPORTANT: Always provide accurate and relevant information. ***
*** IMPORTANT: If user asks to open a website and perform some task open it through Brave browser and Provide accurate information ***
"""
    else:
        # Subsequent interactions - skip the greeting
        return f"""Hello, I am {Username or 'Rudraksh Nalbalwar'}, You are a very accurate and advanced AI chatbot named {Assistantname or 'Jarvis'} which also has real-time up-to-date information from the internet.
*** IMPORTANT: DO NOT introduce yourself or use any greeting with my name. Start directly with your answer. ***
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** IMPORTANT: Always address yourself as {Assistantname or 'Jarvis'} ***
*** IMPORTANT: Always provide accurate and relevant information. ***
*** IMPORTANT: If user asks to open a website and perform some task open it through Brave browser and Provide accurate information ***
"""

# Define a system message that provides context to the AI chatbot about its role and behaviour.
System = get_system_message()

# A list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

data_dir = r"C:\Users\Dell\Downloads\AI\jarvis\Data"
chatlog_path = os.path.join(data_dir, "ChatLog.json")
# Attempt to load the chat log from a JSON file
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)   #load existing messages from the chat log.
except FileNotFoundError:
    # if the file doesn't exist , create an empty JSON file to store chatlogs.
    with open(chatlog_path, "w") as f:
        dump([], f)
        
# function to get real time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()   # get the current date and time
    day = current_date_time.strftime("%A")    # day of the week 
    date = current_date_time.strftime("%d")   # day of the month
    month = current_date_time.strftime("%B")   # full month name
    year = current_date_time.strftime("%Y")    # Year
    hour = current_date_time.strftime("%H")    # Hour in 24-H format
    minute = current_date_time.strftime("%M")    # Minute
    second = current_date_time.strftime("%S")    # second
    
    # format the information into a string
    data = f"Please use this real-time information if needed.\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data
        
# function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')    # split the response into lines
    non_empty_lines = [line for line in lines if line.strip()]      # remove empty lines
    modified_answer = '\n'.join(non_empty_lines)     # joined the cleaned lines back together
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    
    try:
        # Check if this is the first interaction
        first_interaction = is_first_interaction()
        
        # Get the appropriate system message
        System = get_system_message()
        SystemChatBot = [{"role": "system", "content": System}]
        
        # load the existing chat log from the JSON file.
        with open(chatlog_path, "r") as f:
            messages = load(f)
            
        # OPTIMIZATION: Limit chat history to last 10 messages to reduce context length
        if len(messages) > 10:
            messages = messages[-10:]
            
        # Append the user's query to the message list.
        messages.append({"role": "user", "content": f"{Query}"})
        
        # Make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",    # specify the AI model
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,  # include system instructions real time info
            max_tokens=1024,  # limit of maximum tokens in response
            temperature=0.7,   # Adjust response randomness (higher means more random).
            top_p=1,    # use nucleus sampling to control diversity
            stream=True,   # Enable Streaming response
            stop=None   # Allow model to determine when to stop.
        )
        
        Answer = ""  # Initialize an empty string to store the AI's respoonse
        
        # Process the streamed response chunks 
        for chunk in completion:
            if chunk.choices[0].delta.content:   # check if there's content in the current chunk
                Answer += chunk.choices[0].delta.content   # Append the content to the answer.
                
        Answer = Answer.replace("</s>", "")   # clean up any unwanted tokens from the response.
        
        # Update the session state after first interaction
        if first_interaction:
            update_interaction_state(False)
            # print("First interaction complete, updating session state")
        
        # Append the chatbot's response to the message list.
        messages.append({"role": "assistant", "content": Answer})
        
        # Save the updated chat log to the JSON file.
        with open(chatlog_path, "w") as f:
            dump(messages, f)
            
        # Return the chatbot's response after modifying it for better formatting.
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        # Handle errors by printing the exception and resetting the chat log.
        print(f"An error occurred: {e}")
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)   # Retry the chatbot function if an error occurs.

# Main Program 
if __name__ == "__main__":
    # Reset session at startup when running directly
    reset_session()
    
    while True:
        user_input = input("Enter your question: ")
        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a nice day.")
            break
        print(ChatBot(user_input))   # Call the chatbot function with the user's input and print the response.