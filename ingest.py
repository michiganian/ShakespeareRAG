from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
import glob
import re
import chromadb

def read_and_load_data():

    # config vars
    html_directory_path = "shakespeare"
    chromadb_collection_name = 'shakespeare'
    chroma_host = 'localhost'
    chroma_port = 8000

    # make a list of html files
    flist=list_html_files(html_directory_path)
    
    # parse html into documents
    documents = generate_docs(flist)
    print("Document count = "+str(len(documents)))
    
    # split larger Documents into smaller pieces
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = text_splitter.split_documents(documents)
    print("Split documents count = "+str(len(split_docs)))
    
    # convert split document list into the chroma format
    ids = [str(i) for i in range(len(split_docs))]
    metadatas = []
    sentences = []
    for id in ids:
        i = int(id)
        metadatas.append(split_docs[i].metadata)
        sentences.append(split_docs[i].page_content)

    # generate embeddings
    print("Generating embeddings")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedding_model.encode(sentences)

    # setup vector db client
    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    # clear out any existing collection, because I ran this 20 times before getting it working
    try:
        chroma_client.delete_collection(name=chromadb_collection_name)
    except:
        print("Collection "+chromadb_collection_name+" does not exist")
    collection = chroma_client.get_or_create_collection(chromadb_collection_name)

    # load into vector db
    print("Inserting data into ChromaDB")
    collection.add(
        documents=sentences,
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # verify
    print("Chromadb "+chromadb_collection_name+" collection count = "+str(collection.count()))

def list_html_files(dir):
    files = glob.glob(dir+'/**/*.html',recursive = True)
    return files
    
def generate_docs(flist):
    # turn the provided list of html files into langchain Documents
    documents = []
    for f in flist:
        # skip index.html and full.html
        # instead use each scene html file for better chunk splitting conext
        fskip_re = re.compile(r'.+(index|full)\.html')
        fskip_match = fskip_re.match(f)
        if fskip_match:
            continue
        print(f)
        fhandle = open(f, "r")
        fcontent=(fhandle.read())
        fsoup = BeautifulSoup(fcontent, 'html.parser')
        
        # build metadata from title and description
        # title
        if fsoup.title is None:
            ftitle = "no title"
        else:
            ftitle = fsoup.title.string
        
        # td class="play" contains the description
        play_description_td = fsoup.select_one('.play')
        if play_description_td is None:
            play_description = "no description"
        else:
            play_description = play_description_td.get_text()
        
        ftext = fsoup.get_text()
        fdoc = Document(page_content=ftext, metadata={"title": ftitle, "description": play_description}),
        documents.append(fdoc[0])
    return documents

if __name__ == "__main__":
    read_and_load_data()
