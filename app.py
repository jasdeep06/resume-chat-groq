import os
from llama_index.core import StorageContext, load_index_from_storage
import json
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from fastapi import FastAPI
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()



# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Settings.llm = OpenAI(model='gpt-4-turbo-preview')
Settings.llm = Groq(model='llama3-70b-8192')
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")

def description_json_to_str(description):
    new_description = ""
    for key,value in description.items():
        new_description += "{}\n".format(value)
    return new_description



def reformat_description(description,folder,sub_folder):
    new_description = ""
    if folder == 'blogposts':
        blog_title = sub_folder.replace('-',' ')
        new_description += 'Useful for questions from blogpost titled "{}".\n'.format(blog_title)
        new_description += 'Topics covered in this document are:\n{}'
        new_description += description_json_to_str(description)
    elif folder == 'experience-blogs':
        if sub_folder == 'translatetracks-blog':
            new_description += 'Useful for questions related to work experience while CTO at AI dubbing startup TranslateTracks.\n'
            new_description += 'Topics covered in this document are:\n{}'
            new_description += description_json_to_str(description)
        elif sub_folder == 'vinglabs-blog':
            new_description += 'Useful for questions related to work experience while CTO at AI based waste recognition and sorting startup Vinglabs.\n'
            new_description += 'Topics covered in this document are:\n{}'
            new_description += description_json_to_str(description)
    elif folder == 'resume':
        new_description += description["1"]

    return new_description



def create_index_and_description_dict():
    folders_of_interest = ['blogposts','experience-blogs','resume']
    index_dict = {}
    description_dict = {}
    for folder in folders_of_interest:
        sub_folders = os.listdir(os.path.join('cache',folder))
        for sub_folder in sub_folders:
            if sub_folder == 'all':
                continue
            index_dir = os.path.join('cache',folder,sub_folder,'index')
            storage_context = StorageContext.from_defaults(persist_dir=index_dir)
            index = load_index_from_storage(storage_context)
            index_dict[sub_folder] = index
            description_path = os.path.join('cache',folder,sub_folder,'parsed','description.json')
            description = json.load(open(description_path,'r'))
            description_dict[sub_folder] = reformat_description(description,folder,sub_folder)
    return index_dict,description_dict

def init_index():
    index_dict,description_dict = create_index_and_description_dict()
    query_engine_dict = {key:value.as_query_engine() for key,value in index_dict.items()}
    tool_dict = {}
    for key,value in query_engine_dict.items():
        tool_dict[key] = QueryEngineTool.from_defaults(
                    query_engine=query_engine_dict[key],
                description=(
                    description_dict[key]
                ),
            )
    
    query_engine = RouterQueryEngine(
    # selector=LLMMultiSelector.from_defaults(llm=OpenAI(model='gpt-4-turbo-preview'),max_outputs=2),
    selector=LLMMultiSelector.from_defaults(llm=Groq(model='llama3-70b-8192'),max_outputs=2),
    query_engine_tools=[tool_dict[key] for key in tool_dict.keys()],
    verbose=True
    )
    return query_engine

def get_images_from_source_nodes(source_nodes):
    images = []
    for node in source_nodes:
        if "path" in node.metadata.keys():
            images.append(node.metadata["path"].split("\\")[-1] + ".png")
    return images


engine = init_index()

@app.get("/query")
def query_engine(query:str):
    query += "Answer in detail from the context provided. If there are any relevant urls in the context, please provide them as well."
    try:
        response = engine.query(query)
        images = get_images_from_source_nodes(response.source_nodes)
    except ValueError:
        response = "The given question cannot be answered using the provided context."
        images = []

    return {"response":str(response),'images':images}

# if __name__ == '__main__':
#     index_dict,description_dict = create_index_and_description_dict()
#     query_engine_dict = {key:value.as_query_engine() for key,value in index_dict.items()}
#     tool_dict = {}
#     for key,value in query_engine_dict.items():
#         tool_dict[key] = QueryEngineTool.from_defaults(
#                     query_engine=query_engine_dict[key],
#                 description=(
#                     description_dict[key]
#                 ),
#             )
    
#     query_engine = RouterQueryEngine(
#     selector=LLMMultiSelector.from_defaults(llm=OpenAI(model='gpt-4-turbo-preview')),
#     query_engine_tools=[tool_dict[key] for key in tool_dict.keys()],
#     verbose=True
#     )
#     try:
#         response = query_engine.query("Does Jasdeep has any experience with optical configuration in AI projects?")
#     except ValueError:
#         response = "The given question cannot be answered using the provided context."

#     print(response)

        



            