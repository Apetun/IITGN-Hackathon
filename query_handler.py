from dotenv import load_dotenv
load_dotenv()
from text_to_embedding import load_embeddings,get_text,get_text_chunks
from InstructorEmbedding import INSTRUCTOR
import torch,os,re,sqlite3,google.generativeai as genai,faiss


generation_config = {
  "temperature": 0.4,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

model = genai.GenerativeModel(model_name = "gemini-pro",generation_config = generation_config,
                              safety_settings = safety_settings)


prompt_parts_config = [
  """
You are an expert in converting natural language questions to SQL queries that generate a single numeric output. Follow the structure and examples given below to ensure accuracy and case sensitivity in your responses.

There are three tables structured as follows:

Table: Company
  CREATE TABLE "Company" (
    "purchase_date" TEXT,
    "company" TEXT,
    "prefix" TEXT,
    "bond_id" INTEGER,
    "bond_amount" INTEGER,
    "status" TEXT
  );

Table: Political_Party
  CREATE TABLE "Political_Party" (
    "cashout_date" TEXT,
    "political_party" TEXT,
    "prefix" TEXT,
    "bond_id" INTEGER,
    "bond_amount" INTEGER
  );

Table: Joined_Table
  CREATE TABLE "Joined_Table" (
    "purchase_date" TEXT,
    "company" TEXT,
    "prefix" TEXT,
    "bond_id" INTEGER,
    "bond_amount" INTEGER,
    "status" TEXT,
    "cashout_date" TEXT,
    "political_party" TEXT
  );

Examples:
-- Q1: What is the total bond amount encashed by TELUGU DESAM PARTY on 12th April 2019?
OUTPUT: SELECT SUM(bond_amount) FROM Political_Party WHERE political_party = 'TELUGU DESAM PARTY' AND cashout_date = '12/Apr/2019';

-- Q2: What is the total bond amount purchased by CHOUDHARY GARMENTS on 12th April 2019?
OUTPUT: SELECT SUM(bond_amount) FROM Company WHERE company = 'CHOUDHARY GARMENTS' AND purchase_date = '12/Apr/2019';

-- Q3: What is the total number of bonds purchased by ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED on 12th April 2019?
OUTPUT: SELECT count(bond_id) FROM Company WHERE company = 'ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED' AND purchase_date = '12/Apr/2019';

-- Q4: What is the total amount received by AAM AADMI PARTY from DR. MANDEEP SHARMA in the year 2022?
OUTPUT: SELECT SUM(bond_amount) FROM Joined_Table WHERE political_party = 'AAM AADMI PARTY' AND company = 'DR. MANDEEP SHARMA' AND cashout_date >= '01/Jan/2022' AND cashout_date <= '31/Dec/2022';

Instructions:
1. If the exact name of the party or company is not found in the input, find the closest matching name from the context provided.
2. The output should be a single valid SQL query in one line, with no errors, directly executable.
3. Ensure the case of company and political party names matches exactly as provided in the input.
"""
]



def validate_sql_query(query):

    try:
        connection = sqlite3.connect('./working/working.db') 
        cursor = connection.cursor()
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        connection.close()
        return True
    except sqlite3.Error as e:
        return False


def clean_query(query):


    query = query.strip("```")
    query = re.sub(r'\bSQL\b', '', query, flags=re.IGNORECASE)
    query = ' '.join(query.split())

    return query


def handle_query(query):    
    results = []    
    genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))
    query = add_context(query)
    prompt_parts = [prompt_parts_config[0], query]
    ctr = 0
    
    while True:
        response = model.generate_content(prompt_parts)
        if validate_sql_query(clean_query(response.text)):
            results.append(clean_query(response.text))
            break
        ctr+=1
        if ctr>=7:
          results.append("No Answer")
          break
    
    try:
        if results[0] == "No Answer":
          results.append("Answer Not Present")
          return results
        connection = sqlite3.connect("./working/working.db")
        cursor = connection.cursor()
        cursor.execute(results[0])
        single_result = cursor.fetchone()[0]
        results.append(str(single_result))
        connection.close()
        
    except sqlite3.Error as e:
        print(e)
        results.append("Answer Not Present")
    
    return results
 
    
def load_faiss_index(embeddings_file="./working/embeddings.pkl"):
    embeddings = load_embeddings(embeddings_file)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index
  
def encode_query(query):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = INSTRUCTOR('hkunlp/instructor-large').to(device)
    query_embedding = model.encode([query], convert_to_numpy=True)
    return query_embedding

def retrieve_documents(query_embedding, index, text_chunks, top_k=10):
    _, I = index.search(query_embedding, top_k)
    retrieved_docs = [text_chunks[i] for i in I[0]]
    return retrieved_docs

def formulate_prompt(query, retrieved_docs):
    prompt = query + "\n\nContext:\n"
    for doc in retrieved_docs:
        prompt += doc + "\n"
    return prompt
  
  
def add_context(query):
  index = load_faiss_index()
  encoded_query = encode_query(query)
  text = get_text()
  text_chunks = get_text_chunks(text)
  retrieved_docs = retrieve_documents(encoded_query,index,text_chunks)
  
  return formulate_prompt(query,retrieved_docs)
  