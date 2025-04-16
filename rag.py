from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
import chromadb
import ollama
import sys

def run_rag_app():

    # config vars
    ollama_url = 'http://127.0.0.1:11434'
    model="gemma3:12b"
    embed_model = 'all-MiniLM-L6-v2'
    chroma_host = 'localhost'
    chroma_port = 8000
    
    # chroma db handle
    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    embedding_function = SentenceTransformerEmbeddings(model_name=embed_model)
    db = Chroma(
            client=chroma_client,
            collection_name="shakespeare",
            embedding_function=embedding_function,
        )
        
    while True:
        #prompt = "what did the soothsayer say about Charmian?"
        prompt = input("Prompt: ")
        if prompt == "exit":
            sys.exit()
        
        # build context from prompt
        user_prompt = f"""
            ==============================================================
            Based on the above context, please provide the answer to the following question:
            {prompt}
            """

        results = db.similarity_search(prompt)

        results_combined = ''
        for result in results:
            results_combined ='. '.join([results_combined,result.page_content])

        system_context = f"""You are a consultant that provide relevant information from internal documents.
        Generate your response based solely on the provided content.

        CONTENT:
        {results_combined}
        """
        
        # query llm with context and prompt
        ollama_result = query_ollama(ollama_url,model,system_context,user_prompt)
        print(ollama_result)

def query_ollama(ohost,model,system_context,user_prompt):
    ollama_client = ollama.Client(host=ohost)

    ollama_results = ollama_client.chat(model=model, messages=[
    {"role": "system", "content": system_context},            
    {"role": "user", "content": user_prompt}
    ],stream=True)

    print("## Working ")
    ollama_results_combined = ''
    for ollama_result in ollama_results:
        ollama_results_combined =''.join([ollama_results_combined,ollama_result['message']['content']])

    return ollama_results_combined

if __name__ == "__main__":
    run_rag_app()
