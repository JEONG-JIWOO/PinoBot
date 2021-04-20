
import requests ,json
from googletrans import Translator

class HuggingFace:
    def __init__(self,log,URL,KEY):
        self.GPT_API_URL = URL
        self.GPT_HEADERS = {"Authorization": KEY}
        self.log = log

        try:
            self.translator = Translator()
        except:
            self.log.error("pino_huggingface.py: google translate fail")
        else:
            self.log.info('pino_huggingface.py:  google translate success')

    def get_gpt_neo(self,payload):
        data = json.dumps(payload)
        response = requests.request("POST", self.GPT_API_URL, headers=self.GPT_HEADERS, data=data)
        return_data = json.loads(response.content.decode("utf-8"))
        try:
            response = return_data[0]['generated_text'][len(payload):].split(".")
            if len(response[0]) < 10 and len(response) > 1:
                return response[0] + response[1]
            else:
                return response[0]
        except:
            return None

    def translate(self,target,text):
        try:
            result = self.translator.translate(text, dest=target)
            return result.text
        except:
            return None

