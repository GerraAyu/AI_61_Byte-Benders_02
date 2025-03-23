import re
import faiss
import config
import bson
import pdfplumber

from data_services.database import user_col
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_community.vectorstores import FAISS
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.text_splitter import SentenceTransformersTokenTextSplitter

import smtplib
import psycopg2
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


# Initialize model and tools
model = SentenceTransformer('all-MiniLM-L6-v2')
lemmatizer = WordNetLemmatizer()

small_model = ChatMistralAI(model=config.MISTRAL_SMALL, temperature=0)
large_model = ChatMistralAI(model=config.MISTRAL_LARGE, temperature=0)


def get_user_intent(query):
    with open(config.PROMPT_USER_INTENT) as finput:
        base_prompt = finput.read()

    prompt_template = PromptTemplate(
        input_variables=["query"],
        template=(
            base_prompt + "\nQuery: {query}"
        )
    )
    prompt = prompt_template.format(query=query)
    response = small_model.invoke(prompt)
    return response.content


def process_general_query(query, retriever):
    retrieved_docs = retriever.get_relevant_documents(query)

    if retrieved_docs:
        prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template="Using the following documents:\n\n{context}\n\nAnswer the user's query:\n\n{query}"
        )

        # Create a chain with LLM and retrieved documents
        rag_chain = StuffDocumentsChain(
            llm_chain=LLMChain(llm=small_model, prompt=prompt_template),
            document_variable_name="context"
        )

        # Run the chain with retrieved documents
        return {"data": rag_chain.run(input_documents=retrieved_docs, query=query)}



def verify_access(user_id, departments):
    user = user_col.find_document(
        {
            '_id' : bson.ObjectId(user_id)
        }
    )
    return all([user.get(dep + "Access") for dep in departments])


def raise_L1_ticket(user_id,query):
    user = user_col.find_document(
            {
                '_id' : bson.ObjectId(user_id)
            }
        )
    user_details = {
            'user_name': user.get('EmployeeName'),
            'user_department': user.get('Department'),
            'user_job_title': user.get('JobTitle'),
            'user_id': user.get('EmployeeID')
        }

    prompt = f"""
        You are an **ERP Support Assistant** Chatbot for employees at a company.
        Your goal is to **help employees quickly and accurately** with their ERP-related queries.
        This is {query} is a L1 support ticket query
        Make subject and body of the email and send it to the L1 support ticket
        user_details:{user_details}
        Format : Subject : subject
                    Body : body
        make as if the employee has wrote the email
        """
    response = small_model.invoke(prompt)
    subject  = response.content[response.content.find("Subject")+8:response.content.find("Body")-1].strip()
    body = response.content[response.content.find("Body")+5:].strip()
    send_email("2021.ayush.gerra@ves.ac.in",subject,body)
    return "Ticket has been raised at L1 support"


def generate_response(query):
    query = query_llm(query)
    data = execute_sql(query[0].strip())
    if len(str(data)) > 10000: 
        data = data[:5]  

    prompt = f""" 
    You are an **ERP Support Assistant** Chatbot for employees at a company.
    Your goal is to **help employees quickly and accurately** with their ERP-related queries.
        
    **Company ERP Data Available:** 
    {data}
        
    **Employee Query:** {query}
        
    **Your Response Guidelines:**
    - **Be professional and concise** while being friendly.
    - **Provide direct answers** based on the ERP data.
    - If the data is missing or incomplete, **guide the employee on the next steps**.
    - If escalation is needed, **inform the employee that an L1 support ticket has been created**.
    **If the employee asks a question which is not regarding data then please give the subject to the email to be sent to L1 support ticket**

    **Now, respond to the employee's question clearly and helpfully.**"""

    response = large_model.invoke(prompt)
    return response.content
    

def get_all_table_schemas():
    try:
        conn = psycopg2.connect(config.SUPABASE_URL)

        cur = conn.cursor()
        cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()
        schema = {}
        
        if tables:
            for table in tables:
                table_name = table[0]
                
                cur.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}';
                """)
                columns = cur.fetchall()
                schema[table_name] = []
                if columns:
                    for column in columns:
                        schema[table_name].append(column)
                else:
                    print(f"No columns found for table '{table_name}'.")
        else:
            print("No tables found in the public schema.")

        cur.close()
        conn.close()
        return schema 

    except Exception as e:
        print(f"An error occurred: {e}")



def query_llm(query):
    prompt = f"""
    Your task is to write a SQL query that gives output for the following question:{query}
    using the schema {get_all_table_schemas()}
    **Rules**:
        Only provide the query and nothing else only the query
        Do not provide any additional information
        Strictly follow the example for creating the query especially the column names are in inverted commas
    Example:
    SELECT p."SupplierID",pr."ProductID"
    FROM purchase p
    JOIN production pr ON p."MaterialID" = pr."MaterialID"
    where pr."ProductID"='P253';
    """

    response = large_model.invoke(prompt)
    return response.content.splitlines()[1:-1]



def execute_sql(query):
    data = []
    try:
        conn = psycopg2.connect(config.SUPABASE_URL)

        cur = conn.cursor()
        
        cur.execute(query)
        rows = cur.fetchall()

        if rows:
            for row in rows:
                data.append(row)
        else:
            data.append("No rows found.")
        return data 
    except Exception as e:
        print(f"An error occurred: {e}")


def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:  
            smtp.login(config.EMAIL_ADDRESS, "fslr ahai cdhy uzfw")
            smtp.send_message(msg)

        print(f"Email sent successfully to {to_email}!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in ENGLISH_STOP_WORDS]
    return ' '.join(tokens)


def gen_embeddings(texts):
    return model.encode(texts)


def initialize_retriever():
    pdf = pdfplumber.open(config.CODE_CONDUCT)
    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Split text into chunks
    text_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=50, tokens_per_chunk=384)
    text_chunks = text_splitter.split_text(text)

    # Generate embeddings
    embeddings = gen_embeddings(text_chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Store documents
    documents = [Document(page_content=chunk) for chunk in text_chunks]
    docstore_dict = {str(idx): doc for idx, doc in enumerate(documents)}
    docstore = InMemoryDocstore(docstore_dict)
    index_to_docstore_id = {i: str(i) for i in range(len(documents))}

    # Create retriever
    vector_store = FAISS(embedding_function=gen_embeddings, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)
    return vector_store.as_retriever()
