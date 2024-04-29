from openai import OpenAI
from dotenv import load_dotenv
from index import get_pdf_text
load_dotenv()


client = OpenAI()

def call_gpt(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"}
    )

    return chat_completion.choices[0].message.content

import os
import pickle
#get descriptions for different query engines
def get_description_pdfs():
    folders_of_interest = ['blogposts','experience-blogs']
    for folder in folders_of_interest:
        sub_folders = os.listdir(os.path.join('cache',folder))
        for sub_folder in sub_folders:
            print("Processing: ",sub_folder)
            data_path = os.path.join('cache',folder,sub_folder,'parsed','data.pkl')
            data = pickle.load(open(data_path,'rb'))
            text = get_pdf_text(data)
            prompt = text + "\n" + "Give me the topics that this document covers. Do not describe the topics. Respond in json with keys as 1,2,3... and values as the topics."
            response = call_gpt(prompt)
            description_path = os.path.join('cache',folder,sub_folder,'parsed','description.json')
            with open(description_path,'w') as f:
                f.write(response)


if __name__ == "__main__":
    get_description_pdfs()