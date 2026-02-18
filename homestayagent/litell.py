from litellm import completion
import os
from dotenv import load_dotenv

load_dotenv()

response = completion(
    model="ollama/gpt-oss:20b-cloud", 
    messages=[{ "content": "respond in 20 words. who are you?","role": "user"}], 
    api_base=os.getenv("OLLAMA_BASE_URL"),
    headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
)

print(response)

'''
llm = ChatOllama(
    model="gpt-oss:20b-cloud",
    base_url=os.getenv("OLLAMA_BASE_URL"),
    headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
)
print(response)
for chunk in response:
    print(chunk['choices'][0]['delta'])
'''