# ShakespeareRAG

A RAG application using Ollama, ChromaDB, and HTML files.  
  
The complete works of Shakespeare serves as the supplemental data for this POC.  
The generate_docs ingest function is specific to the Shakespeare html files.  
This function would need to be rewritten for other html sources.  
  
Gemma3:12b should run ok on a Mac with Apple silicon and 16GB RAM.  
Choose an appropriate model for other hardware.  
  
At the time of writing, the only python package with an older version requirement is chromadb==0.6.3.  
Anything higher was returning a 500 internal server error from chromadb when creating a collection.  

## Prerequisites
### Ollama running and gemma3:12b pulled, or whatever model you can run
```sh
git clone https://github.com/jmorganca/ollama.git
cd ollama
go build .
./ollama serve &
./ollama pull gemma3:12b
```

### Chroma DB running 
This is not really required. You could use file based storage with Chroma and skip the docker container. I wanted a 'proper' database running.
```sh
docker run -d --name=chromadb -p 8000:8000 -v ~/Documents/rag/chroma_data:/data:z chromadb/chroma
```

### Grab the Shakespeare html files and save in a local folder named 'shakespeare'
Git clone or download and unzip
[https://github.com/TheMITTech/shakespeare/]

## How to run
Edit the config vars if needed in either ingest.py or rag.py

```sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

```sh
python3 ingest.py
```
>	shakespeare/pericles/pericles.3.3.html  
>	...  
>	shakespeare/merchant/merchant.1.3.html  
>	Document count = 1115  
>	Split documents count = 8816  
>	Generating embeddings  
>	Inserting data into ChromaDB  
>	Chromadb shakespeare collection count = 8816  

```sh
python3 rag.py
```
>	Prompt: what did the soothsayer say about Charmian?  
>	\#\# Working  
>	Here's what the Soothsayer said about Charmian, based solely on the provided text:  
>	   "You shall be yet far fairer than you are."  
>  
>	Prompt: exit  
