from groq import Groq     # importing the Groq library to use its API
from json import load, dump     # Importing functions to read and write JSON files
import datetime   # Importing the datetime module for real-time date and time information
from dotenv import dotenv_values    # importing dotenv_values to read environment variables from a .env file

# load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages
messages = []

# Define a system message that provides context to the AI chatbot about its role and behaviour.
System = """"""

# A list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)   #load existing messages from the chat log.
except FileNotFoundError:
    # if the file doesn't exist , create an empty JSON file to store chatlogs.
    with open(r"Data\ChatLog.json", "w") as f:
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
    lines - Answer.split('\n')    # split the response into lines
    non_empty_lines = [line for line in lines if line.strip()]      # remove empty lines
    modified_answer = '\n'.join(non_empty_lines)     # joined the cleaned lines back together
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    
    try:
        # load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
            
        # Append the user's query to the message list.
        messages.append({"role": "User", "content": f"{Query}"})
        
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
        
        