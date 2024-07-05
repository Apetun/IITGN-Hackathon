from dotenv import load_dotenv
load_dotenv()
import os
import sqlite3
import google.generativeai as genai
import re

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
  """You are an expert in converting English questions to SQL code that generate a single numeric output. 
    
    Read and understand the below information step by step:
    Pay attention to the cases and structure of the data values and attribute values.
  
      There are three tables created like this:
      Table: Company
        CREATE TABLE "Company" (
        "purchase_date" TEXT,
        "company" TEXT,
        "prefix" TEXT,
        "bond_id" INTEGER,
        "bond_amount" INTEGER,
        "status" TEXT
        )


        Table: Political_Party
        CREATE TABLE "Political_Party" (
        "cashout_date" TEXT,
        "political_party" TEXT,
        "prefix" TEXT,
        "bond_id" INTEGER,
        "bond_amount" INTEGER
        )


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
        )
        
        Example Values:
        Company:
        purchase_date,company,prefix,bond_id,bond_amount,status
        12/Apr/2019,A B C INDIA LIMITED,TL,11448,1000000,Paid
        12/Apr/2019,ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED,TL,11555,1000000,Paid
        12/Apr/2019,ARIHANT ENTERPRISES,TL,11554,1000000,Paid

        Political_Party:
        cashout_date,political_party,prefix,bond_id,bond_amount
        12/Apr/2019,ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM,OC,775,10000000
        12/Apr/2019,ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM,TL,10466,1000000
        12/Apr/2019,ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM,TL,10423,1000000
        
        Joined_Table:
        purchase_date,company,prefix,bond_id,bond_amount,status,cashout_date,political_party
        12/Apr/2019,A B C INDIA LIMITED,TL,11448,1000000,Paid,25/Apr/2019,BHARATIYA JANATA PARTY
        12/Apr/2019,ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED TL,11556,1000000,Paid,22/Apr/2019,ALL INDIA TRINAMOOL CONGRESS
        12/Apr/2019,ESSEL MINING AND INDS LTD OC,6278,10000000,Paid,20/Apr/2019,BHARATIYA JANATA PARTY

        Sample Input/Output:
        
        -- Q1: What is the total bond amount encashed by TELUGU DESAM PARTY on 12th April 2019?
        OUTPUT : SELECT SUM(bond_amount)
                FROM political_party
                WHERE political_party = 'TELUGU DESAM PARTY'
                AND cashout_date = '12/Apr/2019';

        -- Q2: What is the total bond amount purchased by CHOUDHARY GARMENTS on 12th April 2019?
        OUTPUT:SELECT SUM(bond_amount)
                      FROM company
                      WHERE company = 'CHOUDHARY GARMENTS'
                      AND purchase_date = '12/Apr/2019';

        -- Q3: What is the total number of bonds purchased by ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED on 12th April 2019?
          OUTPUT:SELECT count(bond_id)
                FROM company_table
                WHERE company = 'ACROPOLIS MAINTENANCE SERVICES PRIVATE LIMITED'
                AND purchase_date = '12/Apr/2019';

        -- Q4: What is the total amount received by AAM AADMI PARTY from DR. MANDEEP SHARMA in the year 2022?
          OUTPUT:SELECT SUM(bond_amount)
                FROM joined_table
                WHERE political_party = 'AAM AADMI PARTY'
                AND company = "DR. MANDEEP SHARMA"
                AND cashout_date >= '01/Jan/2022;'
                AND cashout_date <= '31/Dec/2022';
                
                
        NOTE : Output should be a valid sql query in a line text format with no errors which can be directly used as a query with no processing.
        
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
    
    


