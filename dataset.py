from llama_parse import LlamaParse
import os
import pickle
from glob import glob

def parse_and_cache_pdf(path):
    #get basename without extension
    basename = os.path.basename(path).split('.')[0]

    #create cache folder if it doesn't exist
    if not os.path.exists('cache'):
        os.makedirs('cache')
    
    #get parent directory of the file
    parent_dir = os.path.dirname(path).split(os.sep)[-1]

    if not os.path.exists(os.path.join('cache',parent_dir)):
        os.makedirs(os.path.join('cache',parent_dir))
    
    #individual cache path
    cache_path = os.path.join('cache',parent_dir,basename)

    #check if cache exists
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    
    #create the parsed folder if dne
    parsed_path = os.path.join(cache_path,'parsed')
    if not os.path.exists(parsed_path):
        os.makedirs(parsed_path)
    else:
        print("Cache exists, loading from cache...")
        return pickle.load(open(os.path.join(parsed_path,'data.pkl'),'rb')),pickle.load(open(os.path.join(parsed_path,'images.pkl'),'rb'))

    #parse the pdf
    parser = LlamaParse(
    api_key="llx-nO6BMv1gWY9CqX0eUqTF8sKhez2TEs7UD2zG3aFNY1fVPaBD",  # can also be set in your env as LLAMA_CLOUD_API_KEY
    verbose=True)

    json_objs = parser.get_json_result(path)

    image_path = os.path.join(parsed_path,'images')

    if not os.path.exists(image_path):
        os.makedirs(image_path)
    
    images = parser.get_images(json_objs, download_path=image_path)

    #save the parsed data
    with open(os.path.join(parsed_path,'data.pkl'),'wb') as f:
        pickle.dump(json_objs,f)
    
    with open(os.path.join(parsed_path,'images.pkl'),'wb') as f:
        pickle.dump(images,f)

    return json_objs,images

import json 

def parse_and_cache_resume(json_path):

    #create cache folder if it doesn't exist
    if not os.path.exists('cache'):
        os.makedirs('cache')
    
    #get parent directory of the file
    parent_dir = os.path.dirname(json_path).split(os.sep)[-1]

    if not os.path.exists(os.path.join('cache',parent_dir)):
        os.makedirs(os.path.join('cache',parent_dir))
    
    resume_json = json.load(open(json_path,'r'))

    #create an "all" key in resume_json with value as appending all values with prepended key and a newlinw
    resume_json['all'] = '\n'.join([f"{key}\n {value}" for key,value in resume_json.items()])
    


    #keys as individual cache paths and data.pkl as the value in parsed path
    for key in resume_json.keys():

        #individual cache path
        cache_path = os.path.join('cache',parent_dir,key)

        #check if cache exists
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        
        #create the parsed folder if dne
        parsed_path = os.path.join(cache_path,'parsed')
        if not os.path.exists(parsed_path):
            os.makedirs(parsed_path)
        else:
            print("Cache exists, loading from cache...")
            continue

        #save the parsed data
        with open(os.path.join(parsed_path,'data.pkl'),'wb') as f:
            pickle.dump(resume_json[key],f)
        
    


def init_pdfs():
    folders_of_interest = ['blogposts','experience-blogs']
    pdf_paths = [glob(os.path.join('data',folder,'*.pdf')) for folder in folders_of_interest]
    pdf_paths = [item for sublist in pdf_paths for item in sublist]
    for path in pdf_paths:
        print(f"Processing {path}")
        parse_and_cache_pdf(path)

def init_resume():
    folders_of_interest = ['resume']
    json_paths = [glob(os.path.join('data',folder,'*.json')) for folder in folders_of_interest]
    json_paths = [item for sublist in json_paths for item in sublist]
    print(json_paths)
    for path in json_paths:
        print(f"Processing {path}")
        parse_and_cache_resume(path)
    



if __name__ == '__main__':
    init_resume()
    
    
