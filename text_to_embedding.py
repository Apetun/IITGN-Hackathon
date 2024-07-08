from tqdm import tqdm
from langchain.text_splitter import CharacterTextSplitter
from InstructorEmbedding import INSTRUCTOR
import torch,pickle,os,numpy as np

def save_embeddings(embeddings, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(embeddings, f)

def load_embeddings(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
def text_to_embedding():
    text = get_text()
    text_chunks = get_text_chunks(text)
    pickle_embeddings(text_chunks)


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

def pickle_embeddings(text_chunks,embeddings_file='./working/embeddings.pkl'):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    if os.path.exists(embeddings_file):
        print(f"Loading embeddings from {embeddings_file}")
        embeddings = load_embeddings(embeddings_file)
    else:
        model = INSTRUCTOR('hkunlp/instructor-large').to(device)
        batch_size = 32
        embeddings = []

        for i in tqdm(range(0, len(text_chunks), batch_size), desc="Encoding text chunks"):
            batch_chunks = text_chunks[i:i + batch_size]
            batch_embeddings = model.encode(batch_chunks, convert_to_numpy=True)
            embeddings.extend(batch_embeddings)

        embeddings = np.array(embeddings)
        save_embeddings(embeddings, embeddings_file)
        print(f"Embeddings saved to {embeddings_file}")