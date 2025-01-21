import cohere # Import the cohere library for AI services
from rich import print  # Rich library to enhance terminal outputs
from dotenv import dotenv_values # dotenv to load environment varibales from a .env file

# load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve API Key
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a cohere client using the provided API key
co = cohere.Client(api_key=CohereAPIKey)

# Define the list of Recognised function keywords for task categorization
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

#Initialize an empty list to store user messages
messages = []

# Define the preamble that guides the AI model on how to categorize queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open Facebook,' etc.
** Do not answer any query, just decide what kind of query is given to you. **

→ Respond with 'general ( query )' if a query can be answered by a LLM model (conversational AI chatbot) and doesn't require any up-to-date information.
    - Example: If the query is "Who was Akbar?", respond with 'general who was akbar?'
    - Example: If the query is "How can I study more effectively?", respond with 'general how can i study more effectively?'
    - Example: If the query is "Can you help me with this math problem?", respond with 'general can you help me with this math problem?'
    - Example: If the query is "Thanks, I really liked it.", respond with 'general thanks, i really liked it.'
    - Example: If the query is "What is Python programming language?", respond with 'general what is python programming language?'

→ Respond with 'realtime ( query )' if a query cannot be answered by a LLM model (because they don't have realtime data) and requires up-to-date information.
    - Example: If the query is "What is the current time in London?", respond with 'realtime what is the current time in london?'
    - Example: If the query is "Who won the match yesterday?", respond with 'realtime who won the match yesterday?'
    - Example: If the query is "Is it raining right now in New York?", respond with 'realtime is it raining right now in new york?'
    - Example: If the query is "What is the stock price of Tesla at this moment?", respond with 'realtime what is the stock price of tesla at this moment?'
    - Example: If the query is "Are there any flights available to Delhi today?", respond with 'realtime are there any flights available to delhi today?'

→ Respond with 'open (application name or website name)' if a query is asking to open any application like 'open Facebook,' 'open Telegram,' etc.
    - Example: If the query is "Open Facebook.", respond with 'open facebook'
    - Example: If the query is "Launch YouTube.", respond with 'open youtube'
    - Example: If the query is "Can you open my email app?", respond with 'open email app'
    - Example: If the query is "Start WhatsApp.", respond with 'open whatsapp'
    - Example: If the query is "Open Google Drive for me.", respond with 'open google drive'

→ Respond with 'close (application name)' if a query is asking to close any application like 'close Notepad,' 'close Facebook,' etc.
    - Example: If the query is "Close Notepad.", respond with 'close notepad'
    - Example: If the query is "Can you close Chrome for me?", respond with 'close chrome'
    - Example: If the query is "Shut down Spotify.", respond with 'close spotify'
    - Example: If the query is "End the Zoom app.", respond with 'close zoom'
    - Example: If the query is "Close Telegram.", respond with 'close telegram'

→ Respond with 'play (song name)' if a query is asking to play any song like 'play Afsanay by VS,' 'play Let Her Go,' etc.
    - Example: If the query is "Play Shape of You.", respond with 'play shape of you'
    - Example: If the query is "Can you play Believer by Imagine Dragons?", respond with 'play believer by imagine dragons'
    - Example: If the query is "Play Sunflower from Spider-Man.", respond with 'play sunflower from spider-man'
    - Example: If the query is "Put on Blinding Lights.", respond with 'play blinding lights'
    - Example: If the query is "Play Dynamite by BTS.", respond with 'play dynamite by bts'

→ Respond with 'generate image (image prompt)' if a query is requesting to generate an image with a given prompt like 'generate image of a lion,' etc.
    - Example: If the query is "Generate an image of a lion.", respond with 'generate image an image of a lion'
    - Example: If the query is "Make a picture of a futuristic city.", respond with 'generate image a futuristic city'
    - Example: If the query is "Create a sunset over mountains.", respond with 'generate image a sunset over mountains'
    - Example: If the query is "Draw a robot in a jungle.", respond with 'generate image a robot in a jungle'
    - Example: If the query is "Generate an image of a fantasy dragon.", respond with 'generate image a fantasy dragon'

→ Respond with 'system (task name)' if a query is asking to perform system-related tasks like mute, unmute, volume up, volume down, etc.
    - Example: If the query is "Mute the volume.", respond with 'system mute'
    - Example: If the query is "Turn the volume up.", respond with 'system volume up'
    - Example: If the query is "Can you lock the system?", respond with 'system lock'
    - Example: If the query is "Take a screenshot.", respond with 'system take a screenshot'
    - Example: If the query is "Restart the computer.", respond with 'system restart'

→ Respond with 'content (topic)' if a query is asking to write any type of content like applications, codes, emails, or anything else about a specific topic.
    - Example: If the query is "Write an email to my manager.", respond with 'content email to manager'
    - Example: If the query is "Draft a resignation letter.", respond with 'content resignation letter'
    - Example: If the query is "Create Python code for a calculator.", respond with 'content python code for a calculator'
    - Example: If the query is "Write an essay about climate change.", respond with 'content essay about climate change'
    - Example: If the query is "Generate a blog post about AI trends.", respond with 'content blog post about ai trends'

→ Respond with 'google search (topic)' if a query is asking to search a specific topic on Google.
    - Example: If the query is "Search for best laptops under $1000.", respond with 'google search best laptops under $1000'
    - Example: If the query is "Find the nearest Italian restaurant.", respond with 'google search nearest italian restaurant'
    - Example: If the query is "Look up benefits of yoga.", respond with 'google search benefits of yoga'
    - Example: If the query is "Search for latest news in technology.", respond with 'google search latest news in technology'
    - Example: If the query is "Find how to bake a cake.", respond with 'google search how to bake a cake'

→ Respond with 'youtube search (topic)' if a query is asking to search a specific topic on YouTube.
    - Example: If the query is "Search for cooking tutorials on YouTube.", respond with 'youtube search cooking tutorials'
    - Example: If the query is "Look up guitar lessons.", respond with 'youtube search guitar lessons'
    - Example: If the query is "Find workout videos for beginners.", respond with 'youtube search workout videos for beginners'
    - Example: If the query is "Search for TED Talks about leadership.", respond with 'youtube search ted talks about leadership'
    - Example: If the query is "Look up funny cat videos.", respond with 'youtube search funny cat videos'

** If the query is asking to perform multiple tasks like 'open Facebook, Telegram, and close WhatsApp,' respond with 'open facebook, open telegram, close whatsapp.' **

** If the user is saying goodbye or wants to end the conversation like 'bye Jarvis,' respond with 'exit.' **

** Respond with 'general ( query )' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. **

"""

# Define a chat history with predefined user-chatbot interaction for context
ChatHistory = [
    {"role": "User", "message": "how are you"},
    {"role": "Chatbot", "message": "general how are you"},
    {"role": "User", "message": "do you like pizza"},
    {"role": "Chatbot", "message": "general do you like pizza"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that I havea dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me"},
    {"role": "Chatbot", "message": "general chat with me"},
]

# define the main function for decision making on queries

def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "User", "content": f'{prompt}'})
    
    # Create a streaming chat session with the cohere model.
    stream = co.chat_stream(
        model='command-r-plus',  # specify the cohere model to use
        message=prompt,   # pass the user's query
        temperature=0.7,  # set the creativity level of the model
        chat_history=ChatHistory,  # Provide the predefined chat history for context
        prompt_truncation='OFF',   # ensure the prompt is not truncated
        connectors=[],   # No additional connectors are usedd
        preamble=preamble   # pass the detailed instruction preamble
    )
    