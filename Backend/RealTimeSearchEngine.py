import os
import time
import requests
from duckduckgo_search import DDGS
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import yfinance as yf  # For stock prices
import re  # For regular expressions

# Load environment variables from the .env file.
env_vars = dotenv_values(r"C:\Users\Dell\Downloads\AI\jarvis\.env")

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")   
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define enhanced system instructions for better information extraction
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.

*** INFORMATION EXTRACTION INSTRUCTIONS ***
1. Always extract SPECIFIC DATA from search results - don't just refer to websites.
2. For factual queries (prices, statistics, news, events, etc.), clearly provide the exact information.
3. Format your answers professionally with proper punctuation and grammar.
4. When answering questions about current events or data, cite the source of information.
5. If multiple sources have different information, acknowledge the differences and provide the most recent data.
6. DO NOT say "I don't have real-time data" if the search results contain the information.
7. DO NOT suggest websites unless specifically asked - extract and provide the information directly.
8. Present numerical data clearly and precisely without ambiguity.
9. For time-sensitive information like stock prices, mention when the data was reported.
10. When answering questions about real-time data, specify that the information is current as of today.
11. Be concise and direct in your responses.
"""

# Try to load the chat log from a JSON file.
data_dir = r"C:\Users\Dell\Downloads\AI\jarvis\Data"
os.makedirs(data_dir, exist_ok=True)  # Create directory if it doesn't exist
chatlog_path = os.path.join(data_dir, "ChatLog.json")
try: 
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chatlog_path, "w") as f:
        dump([], f)

# Function to get stock prices
def get_stock_price(symbol_or_name):
    # Map of common company names to their stock symbols
    company_map = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "meta": "META",
        "facebook": "META",
        "netflix": "NFLX",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "amazon": "AMZN",
        "walmart": "WMT",
        "disney": "DIS",
        "coca cola": "KO",
        "coca-cola": "KO",
        "pepsi": "PEP",
        "pepsico": "PEP",
        "mcdonald's": "MCD",
        "mcdonalds": "MCD",
        "starbucks": "SBUX",
        "nike": "NKE",
        "ibm": "IBM",
        "intel": "INTC",
        "amd": "AMD",
        "cisco": "CSCO",
        "oracle": "ORCL",
        "salesforce": "CRM",
        "adobe": "ADBE",
        "twitter": "X",
        "uber": "UBER",
        "lyft": "LYFT",
        "airbnb": "ABNB",
        "spotify": "SPOT",
        "tiktok": "BDNCE",  # ByteDance (private)
        "snapchat": "SNAP",
        "snap": "SNAP",
    }
    
    # Check if input is a company name
    symbol = symbol_or_name.upper()
    if symbol_or_name.lower() in company_map:
        symbol = company_map[symbol_or_name.lower()]
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('regularMarketPrice') or info.get('currentPrice')
        previous_close = info.get('previousClose')
        day_high = info.get('dayHigh')
        day_low = info.get('dayLow')
        volume = info.get('volume')
        market_cap = info.get('marketCap')
        
        if not current_price:
            return None
            
        result = f"📈 STOCK DATA FOR: {symbol}\n\n"
        result += f"Current Price: ${current_price:.2f}\n"
        if previous_close:
            change = current_price - previous_close
            percent_change = (change / previous_close) * 100
            result += f"Previous Close: ${previous_close:.2f}\n"
            result += f"Change: {'+' if change >= 0 else ''}{change:.2f} ({'+' if percent_change >= 0 else ''}{percent_change:.2f}%)\n"
        if day_high:
            result += f"Day Range: ${day_low:.2f} - ${day_high:.2f}\n"
        if volume:
            result += f"Volume: {volume:,}\n"
        if market_cap:
            result += f"Market Cap: ${market_cap:,}\n"
            
        result += f"\nData retrieved from Yahoo Finance as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return result
    except Exception as e:
        print(f"Error retrieving stock data: {e}")
        return None

# Function to get weather information
def get_weather(location):
    try:
        # Format the query specifically for weather
        weather_query = f"current weather in {location} temperature conditions forecast"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(weather_query, max_results=3))
            
        if not results:
            return None
            
        # Extract temperatures using regex
        temps = []
        for result in results:
            body = result.get('body', '')
            # Look for temperature patterns like 72°F, 22°C, etc.
            temp_matches = re.findall(r'(\d+)[°º]([CF])', body)
            temps.extend(temp_matches)
            
        # Extract weather conditions
        conditions = []
        weather_terms = ['sunny', 'cloudy', 'rainy', 'stormy', 'snowy', 'foggy', 
                        'clear', 'overcast', 'showers', 'thunderstorm', 'snow', 
                        'rain', 'fog', 'mist', 'windy', 'hot', 'cold', 'warm', 'cool']
        
        for result in results:
            body = result.get('body', '').lower()
            for term in weather_terms:
                if term in body and term not in conditions:
                    conditions.append(term)
                    
        # Format the weather information
        weather_info = f"🌤️ WEATHER FOR: {location.upper()}\n\n"
        
        if temps:
            weather_info += "Temperature: "
            for temp, unit in temps[:2]:  # Just show a couple of temperature readings
                weather_info += f"{temp}°{unit} "
            weather_info += "\n"
            
        if conditions:
            weather_info += f"Conditions: {', '.join(conditions[:3])}\n"  # Show up to 3 conditions
            
        # Include the original results
        weather_info += "\nSource Information:\n"
        for i, result in enumerate(results):
            weather_info += f"- {result.get('body', 'No description')}\n"
            
        weather_info += f"\nData retrieved as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return weather_info
    except Exception as e:
        print(f"Error retrieving weather data: {e}")
        return None

# Function to get news information
def get_news(topic):
    try:
        # Format the query specifically for news
        news_query = f"{topic} latest news today"
        
        with DDGS() as ddgs:
            news_results = list(ddgs.news(news_query, max_results=5))
            
        if not news_results:
            return None
            
        # Format the news information
        news_info = f"📰 LATEST NEWS ABOUT: {topic.upper()}\n\n"
        
        for i, result in enumerate(news_results):
            news_info += f"{i+1}. {result.get('title', 'No title')}\n"
            news_info += f"   {result.get('body', 'No description')}\n"
            news_info += f"   Source: {result.get('source', 'Unknown')} | Date: {result.get('date', 'Unknown date')}\n\n"
            
        news_info += f"\nNews retrieved as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return news_info
    except Exception as e:
        print(f"Error retrieving news data: {e}")
        return None

# Function to get sports scores and match information
def get_sports_score(query):
    try:
        # Extract team names and sport type
        team_pattern = r'(score|result|match)\s+(?:of|for|between)?\s+([a-zA-Z\s]+)'
        sport_terms = ["cricket", "football", "soccer", "basketball", "tennis", "baseball", "hockey", "nba", "nfl", "ipl", "match"]
        
        sport_type = None
        for term in sport_terms:
            if term in query.lower():
                sport_type = term
                break
                
        team_name = None
        match = re.search(team_pattern, query.lower())
        if match:
            team_name = match.group(2).strip()
            
        # If we couldn't extract team name, try to find capitalized words
        if not team_name:
            words = query.split()
            for word in words:
                if word[0].isupper() and len(word) > 2 and word.lower() not in ["what", "who", "when", "where", "how", "did", "was", "is"]:
                    team_name = word
                    break
        
        # Create specific search query for sports scores
        search_query = f"{team_name or ''} {sport_type or ''} live score today result"
        
        # Perform focused search
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=5))
            
        if not results:
            return None
            
        # Format sports information
        sports_info = f"🏆 MATCH INFORMATION: {team_name.upper() if team_name else 'LATEST SPORTS'} SCORE\n\n"
        
        # Extract scores using regex patterns for different formats
        score_patterns = [
            r'(\d+)[-\/](\d+)',  # Basic score format like 3-0, 2/1
            r'(\d+)[^\d]+(\d+)\s+runs',  # Cricket scores
            r'(\d+)\s*for\s*(\d+)',  # Cricket format like 180 for 4
            r'(\d+)\/(\d+)',  # IPL/Cricket format 180/4
            r'([a-zA-Z\s]+)\s+(\d+)[\s-]+(\d+)\s+([a-zA-Z\s]+)'  # Team1 3 - 1 Team2 format
        ]
        
        scores_found = []
        for result in results:
            body = result.get('body', '')
            title = result.get('title', '')
            content = title + " " + body
            
            for pattern in score_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    scores_found.extend(matches)
        
        # Add extracted scores
        if scores_found:
            sports_info += "Extracted Scores:\n"
            for i, score in enumerate(scores_found[:3]):  # Show up to 3 score matches
                if len(score) == 2:
                    sports_info += f"• Score: {score[0]}-{score[1]}\n"
                elif len(score) == 4:
                    sports_info += f"• {score[0]} {score[1]}-{score[2]} {score[3]}\n"
                    
        # Include raw source data for context
        sports_info += "\nMatch Details:\n"
        for i, result in enumerate(results):
            sports_info += f"{i+1}. {result.get('title', 'No title')}\n"
            sports_info += f"   {result.get('body', 'No description')}\n\n"
            
        sports_info += f"\nData retrieved as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return sports_info
    except Exception as e:
        print(f"Error retrieving sports data: {e}")
        return None

# Function to perform optimized searches for different types of queries
def EnhancedSearch(query):
    query_lower = query.lower()
    
    # Check for stock price queries
    if any(term in query_lower for term in ["stock price", "share price", "stock value", "stock market", "shares of"]):
        # Try to identify the company name
        for company in ["apple", "microsoft", "amazon", "google", "meta", "facebook", "netflix", 
                        "tesla", "nvidia", "amazon", "walmart", "disney", "coca cola", "coca-cola",
                        "pepsi", "pepsico", "mcdonald's", "mcdonalds", "starbucks", "nike", "ibm",
                        "intel", "amd", "cisco", "oracle", "salesforce", "adobe", "twitter", 
                        "uber", "lyft", "airbnb", "spotify", "tiktok", "snapchat", "snap"]:
            if company in query_lower:
                stock_data = get_stock_price(company)
                if stock_data:
                    return stock_data
                break
    if any(term in query_lower for term in ["score", "match", "game", "vs", "versus", "playing", "won", "lost", "draw", "points", "cricket", "football", "ipl"]):
        sports_data = get_sports_score(query)
        if sports_data:
            return sports_data       
        # If no specific company found but it's a stock query, try to extract a company/symbol
        words = query_lower.split()
        for word in words:
            if word.isalpha() and len(word) >= 2 and word not in ["what", "is", "the", "of", "for", "stock", "price", "current", "today", "now"]:
                stock_data = get_stock_price(word)
                if stock_data:
                    return stock_data
    
    # Check for weather queries
    if "weather" in query_lower:
        # Try to extract location
        location_patterns = [
            r"weather\s+in\s+([a-zA-Z\s]+)",  # "weather in New York"
            r"weather\s+for\s+([a-zA-Z\s]+)",  # "weather for Chicago"
            r"weather\s+([a-zA-Z\s]+)",  # "weather London"
            r"([a-zA-Z\s]+)\s+weather"   # "London weather"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                weather_data = get_weather(location)
                if weather_data:
                    return weather_data
                break
    
    # Check for news queries
    if any(term in query_lower for term in ["news", "latest", "current events", "happened", "update", "headlines"]):
        # Extract the topic
        topic = query_lower
        for term in ["news", "latest", "current events", "happened", "update", "headlines", "what's", "what is", "tell me", "about"]:
            topic = topic.replace(term, "").strip()
            
        if topic:
            news_data = get_news(topic)
            if news_data:
                return news_data
    
    # For general queries, use the enhanced search approach
    try:
        # Enhance query based on type of information requested
        enhanced_query = query
        
        # Perform multiple search types for better results
        results = []
        
        # Standard text search
        with DDGS() as ddgs:
            text_results = list(ddgs.text(enhanced_query, max_results=5))
            results.extend(text_results)
            
        # Format the search results for optimal information extraction
        Answer = f"SEARCH RESULTS FOR: '{query}'\n\n"
        
        for i, result in enumerate(results):
            Answer += f"SOURCE {i+1}:\n"
            Answer += f"Title: {result.get('title', 'No title')}\n"
            Answer += f"Content: {result.get('body', 'No description')}\n"
            Answer += f"Link: {result.get('href', 'No link')}\n\n"
            
        Answer += "\nINSTRUCTIONS FOR PROCESSING THESE RESULTS:\n"
        Answer += "1. Extract the SPECIFIC information requested in the user's query.\n"
        Answer += "2. Present the information directly and clearly.\n"
        Answer += "3. Cite which source you used for the information.\n"
        Answer += "4. Don't mention that you're processing search results - just provide the answer.\n"
        
        return Answer
    except Exception as e:
        # If search fails, fall back to a direct model response
        return f"I couldn't retrieve search results for '{query}'. I'll answer based on my knowledge instead. Error: {str(e)[:100]}"

# Function to clean up the answer by removing empty lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# Predefined Chatbot Conversation system message
SystemChatBot = [
    {"role": "system", "content": System}
]

# Function to get real time information like the current date and time
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B") 
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"CURRENT DATE AND TIME:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# Function to handle real time search and response generation
def RealtimeSearchEngine(prompt, retry_count=2):
    global SystemChatBot, messages
    
    if retry_count <= 0:
        return "I'm having trouble processing your request. Please try again later."
    
    try:
        # Load the chat log from the json file
        with open(chatlog_path, "r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": f"{prompt}"})
        
        # Get enhanced search results
        search_results = EnhancedSearch(prompt)
        
        # Generate a response using the Groq client with improved message structure
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": System},
                {"role": "system", "content": Information()},
                {"role": "system", "content": search_results},
                {"role": "system", "content": "IMPORTANT: Extract and present the specific information requested. Be direct and concise."},
                {"role": "user", "content": f"{prompt}"}
            ],
            temperature=0.3,  # Lower temperature for more factual, precise responses
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )     
        
        Answer = ""
        
        # Concatenate response chunks from the streaming output
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        # Clean up the response
        Answer = Answer.strip().replace("</s>", "")
        
        # Remove any mentions of "search results" or "sources" from the final answer
        Answer = re.sub(r'based on (?:the |)(?:search |)results', '', Answer, flags=re.IGNORECASE)
        Answer = re.sub(r'according to the search results', '', Answer, flags=re.IGNORECASE)
        Answer = re.sub(r'from the search results', '', Answer, flags=re.IGNORECASE)
        Answer = re.sub(r'from (?:the |)source[s]? \d+', '', Answer, flags=re.IGNORECASE)
        
        messages.append({"role": "assistant", "content": Answer})
        
        # Save the updated chat log back to the JSON file
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)
            
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return RealtimeSearchEngine(prompt, retry_count-1)

# Main program
if __name__ == "__main__":
    print("Real-time Search Engine started. Type 'exit' to quit.")
    while True:
        prompt = input("Enter your query: ")
        if prompt.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a nice day.")
            break
        print(RealtimeSearchEngine(prompt))