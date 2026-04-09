import os
import requests
from dotenv import load_dotenv
load_dotenv()
import pymysql
from ollama import Client
from langchain.tools import tool


OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

#--------------------------
# Web Search Tool
#---------------------------
ollama_client = Client(host="https://ollama.com",
                    headers={'Authorization':f"Bearer {OLLAMA_API_KEY}"})

@tool('live_web_search')
def live_web_search(query: str):
    """ Perform a web search using Ollama Cloud Web search API
        Input: Search query String
        Output: Return a json string of top 3 results. Restrict to 5-8 lines. 
    """
    response = ollama_client.web_search(query=query,max_results=3)
    results = response.results
    return results

@tool('mysql_query_tool')
def mysql_query_tool(query: str):
    """Execute read-only MySQL queries on ecommerce DB"""
    return safe_query(query)

def safe_query(query: str):
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER"]

    if any(word in query.upper() for word in forbidden):
        return "❌ Only SELECT queries allowed"

    return query_mysql(query)



def query_mysql(query: str):
    conn = pymysql.connect(
        host = os.getenv("MYSQL_HOST"),
        port=  int(os.getenv("MYSQL_PORT")),
        user=  os.getenv("MYSQL_USER"),
        password=  os.getenv("MYSQL_PWD"),
        database="ecommerce",
        ssl = {'ssl':{}}
    )
    
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    
    conn.close()
    return result