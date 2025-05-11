from openai import OpenAI
import requests
from flask import Flask, request


api_base = "https://api.deepseek.com"
api_key = "sk-bcc2decd51d8463887c694430ed7c3f1"
prompt = "You're an XML file generator that you'll generate the corresponding XML file with the payload information that I've given you. Format requirements: The main attribute is 'Vulnerability', which contains the 'Init' attribute. The 'Name' attribute (the name of the vulnerability), 'Stages' attribute (the number of Stages, default 1), 'Ports' attribute (the port number exploited by the vulnerability), 'WelcomeMess' attribute (default empty), and 'DefaultReply' attribute (default random) (optional)) are nested elements in the 'Init' attribute. You do not have to explain or output other message other than the XML message."

def get_response(message):
       client = OpenAI(
             api_key=api_key,
             base_url=api_base
       )
       messages = [{"role": "system", "content": prompt}, {"role": "user", "content": message},]
       try:
          response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
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
    app.run(host='127.0.0.1', port=12347)
        		
        

