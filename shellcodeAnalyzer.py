from openai import OpenAI
import requests
from flask import Flask, request


api_base = "https://api.chatanywhere.tech"
api_key = "sk-iALwU7cnvOufvsV9cZray5cac4sXuNDfzveOv93f1Nbv5qWo"
prompt = "You are a shellcode analyzer that is asked to extract only one target machine's legal IP address and legal port number. You have to decode and extract them acurately from the provided shellcode based on their possible encoded methods. You have to noticed that they are especially used for a reverse connection purpose and they are not host's ip address and port. Carefully, you should only return two properties in a string array, the first element is the target's IP address and the second element is the target's port number. You should not output any other text that is not part of this string array"

def get_response(message):
       client = OpenAI(
             api_key=api_key,
             base_url=api_base
       )
       messages = [{"role": "system", "content": prompt}, {"role": "user", "content": message},]
       try:
          response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
          )
          return response.choices[0].message.content
       except Exception as e:
      		print(e)
      		return 0
      		
app = Flask(__name__)
@app.route('/execute', methods=['GET'])
def execute_command_get():
    command = request.args.get('command')
    output = get_response(command)
    if output==0:
           return False
    return output
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12346)
        		
        

