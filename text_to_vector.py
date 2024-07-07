from tqdm import tqdm
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from InstructorEmbedding import INSTRUCTOR
import numpy as np

    
def text_to_vector():
    
    def get_text():
        file_path = './working/output.txt'
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    
    
    def get_text_chunks(text):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        ) 
        chunks = text_splitter.split_text(text)
        return chunks
    
    def get_vectorstore(text_chunks):

        model = INSTRUCTOR('hkunlp/instructor-large')

        batch_size = 32 
        embeddings = []
        
        for i in tqdm(range(0, len(text_chunks), batch_size), desc="Encoding text chunks"):
            batch_chunks = text_chunks[i:i + batch_size]
            batch_embeddings = model.encode(batch_chunks, convert_to_numpy=True)
            embeddings.extend(batch_embeddings)

        embeddings = np.array(embeddings)
        
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore
    
    
    text = get_text()
    chunks = get_text_chunks(text)
    vectorstore = get_vectorstore(chunks)
    
    print(vectorstore)
    
    
