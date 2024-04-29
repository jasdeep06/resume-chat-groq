from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.schema import ImageDocument
from llama_index.core.schema import TextNode
import pickle
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.core.response.notebook_utils import display_source_node
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage
import shutil
load_dotenv()


def get_pdf_text(data_obj):
    pdf_text = ''
    for page in data_obj[0]['pages']:
        pdf_text += page['text']
    
    return pdf_text

def create_documents_from_text(text):
    docs = [Document(text=text)]
    return docs

def add_metadata_to_document(documents,author,title ):
    documents[0].metadata['author'] = author
    documents[0].metadata['title'] = title
    return documents

def create_base_nodes(documents,chunk_size,chunk_overlap):
    node_parser = SentenceSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    base_nodes = node_parser.get_nodes_from_documents(documents)
    for idx,node in enumerate(base_nodes):
        node.id_ = "node-{}".format(str(idx))
    return base_nodes


def create_smaller_index_nodes(base_nodes,chunk_sizes):
    parsers = [SentenceSplitter(chunk_size = c,chunk_overlap=0) for c in chunk_sizes]

    all_nodes = []
    for base_node in base_nodes:
        for parser in parsers:
            sub_nodes = parser.get_nodes_from_documents([base_node])
            sub_inodes = [
                IndexNode.from_text_node(sn,index_id=base_node.node_id) for sn in sub_nodes
            ]
            all_nodes.extend(sub_inodes)

        original_node = IndexNode.from_text_node(base_node,index_id = base_node.node_id)
        all_nodes.append(original_node)

    return all_nodes

def get_image_text_nodes(data_objs,image_dicts,image_width_threshold,llm_prompt,metadata,cache_path,cache=False,load_from_cache=True):
    
    if os.path.exists(cache_path) and load_from_cache:
        cached_meta_dict = pickle.load(open(cache_path,'rb'))
        img_text_nodes = []
        for image_path_gpt_dict in cached_meta_dict:
            text_node = TextNode(
                text=image_path_gpt_dict['response'],
                metadata=metadata
            )
            img_text_nodes.append(text_node)
        return img_text_nodes
    elif load_from_cache:
        raise Exception("Cache path does not exist")

    openai_mm_llm = OpenAIMultiModal( model="gpt-4-vision-preview", max_new_tokens=300)
    img_text_nodes = []
    img_meta_dicts = []
    for image_dict in image_dicts:
        if image_dict['width'] > image_width_threshold and image_dict['height'] > 100:
            print("Processing image: ",image_dict['path'])
            image_path_gpt_dict = {}
            image_path_gpt_dict['path'] = image_dict['path']
            metadata['path'] = image_dict['path']
            image_doc = ImageDocument(image_path=image_dict["path"])
            response = openai_mm_llm.complete(
                prompt="""
                {}
                {}
                """.format(llm_prompt,data_objs[0]['pages'][image_dict['page_number']-1]["md"])
                ,
                image_documents=[image_doc],
            )
            image_path_gpt_dict['response'] = str(response)
            image_path_gpt_dict['context'] = data_objs[0]['pages'][image_dict['page_number']-1]["md"]
            print(str(response))
            text_node = TextNode(
                text=str(response),
                #metadata={"path": image_dict["path"],"author":"Jasdeep Singh Chhabra","blog_title":"Towards Backpropagation"}
                metadata=metadata
            )
            img_text_nodes.append(text_node)
            img_meta_dicts.append(image_path_gpt_dict)
    
    if cache:
        pickle.dump(img_meta_dicts,open(cache_path,'wb'))

    return img_text_nodes

def get_blog_title_from_path(cache_path):
    return cache_path.split(os.sep)[-1].replace("-"," ")

def get_resume_title_from_path(cache_path):
    section = cache_path.split(os.sep)[-1]
    if section == 'all':
        return "Jasdeep Singh Chhabra's Full Resume"
    else :
        return "Jasdeep Singh Chhabra's " + section 



def create_index(cache_path,overwrite_index=False,overwrite_image_nodes=False):
    index_path = os.path.join(cache_path,'index')
    if overwrite_index:
        if os.path.exists(index_path):
            print("Index already exists, deleting and creating new index...")
            shutil.rmtree(index_path)

    if not os.path.exists(index_path):
        os.makedirs(index_path)
    else:
        print("Index already exists, loading from cache...")
        return
    embed_model = OpenAIEmbedding(model="text-embedding-3-large")

    parse_path = os.path.join(cache_path,'parsed')
    data_objs = pickle.load(open(os.path.join(parse_path,'data.pkl'),'rb'))
    print(data_objs)
    image_dicts = pickle.load(open(os.path.join(parse_path,'images.pkl'),'rb'))
    pdf_text = get_pdf_text(data_objs)
    documents = create_documents_from_text(pdf_text)
    documents = add_metadata_to_document(documents,author="Jasdeep Singh Chhabra",title=get_blog_title_from_path(cache_path))
    base_nodes = create_base_nodes(documents,chunk_size=1024,chunk_overlap=0)
    all_nodes = create_smaller_index_nodes(base_nodes,chunk_sizes=[256,512])
    img_text_nodes = get_image_text_nodes(data_objs,image_dicts,image_width_threshold=300,
                                          llm_prompt="I have an image from a pdf and following is the text on the same page as the image. Explain the image in detail but do not let the me know that you are describing an image.",
                                          metadata={"author":"Jasdeep Singh Chhabra",
                                                    "blog_title":get_blog_title_from_path(cache_path)},
                                                    cache_path=os.path.join(parse_path,'img_meta.pkl'),cache=True,load_from_cache= not overwrite_image_nodes)
    all_nodes.extend(img_text_nodes)


    index = VectorStoreIndex(all_nodes,embed_model=embed_model)
    # retriever = index.as_retriever(similarity_top_k=2,embed_model=embed_model,verbose=True)
    # retrievals = retriever.retrieve(
    #     'What is this document about?'
    # )
    # print(str(retrievals))
    
    

    index.storage_context.persist(index_path)

    # storage_context = StorageContext.from_defaults(persist_dir="test")

    # new_index = load_index_from_storage(storage_context)

    # new_retriever = new_index.as_retriever(similarity_top_k=2,embed_model=embed_model,verbose=True)
    # retrievals = new_retriever.retrieve(
    #     'What is this document about?'
    # )
    # print(str(retrievals))

# create_index("cache\\blogposts\\towards-backpropagation",overwrite_index=True,overwrite_image_nodes=True)

def create_index_resume(cache_path,overwrite_index=False):
    index_path = os.path.join(cache_path,'index')
    if overwrite_index:
        if os.path.exists(index_path):
            print("Index already exists, deleting and creating new index...")
            shutil.rmtree(index_path)

    if not os.path.exists(index_path):
        os.makedirs(index_path)
    else:
        print("Index already exists, loading from cache...")
        return
    
    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    parse_path = os.path.join(cache_path,'parsed')
    text = pickle.load(open(os.path.join(parse_path,'data.pkl'),'rb'))
    documents = create_documents_from_text(text)
    documents = add_metadata_to_document(documents,author="Jasdeep Singh Chhabra",title=get_resume_title_from_path(cache_path))
    base_nodes = create_base_nodes(documents,chunk_size=1024,chunk_overlap=0)
    index = VectorStoreIndex(base_nodes,embed_model=embed_model)
    index.storage_context.persist(index_path)


def init_pdfs():
    # folders_of_interest = ['blogposts','experience-blogs']
    folders_of_interest = ['experience-blogs']
    for folder in folders_of_interest:
        sub_folders = os.listdir(os.path.join('cache',folder))
        for sub_folder in sub_folders:
            create_index(os.path.join('cache',folder,sub_folder),overwrite_image_nodes=True,overwrite_index=True)
            print("Index created for: ",sub_folder)

def init_resume():
    folders_of_interest = ['resume']
    for folder in folders_of_interest:
        sub_folders = os.listdir(os.path.join('cache',folder))
        for sub_folder in sub_folders:
            if sub_folder != 'skills':
                continue
            create_index_resume(os.path.join('cache',folder,sub_folder),overwrite_index=True)
            print("Index created for: ",sub_folder)




if __name__ == "__main__":
    init_resume()
    