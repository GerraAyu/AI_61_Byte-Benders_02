import re
import faiss
import config
import pdfplumber

from data_services.database import user_col
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain.docstore import InMemoryDocstore
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.text_splitter import SentenceTransformersTokenTextSplitter


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
    user = user_col.find_one(
        {
            'EmployeeID' : user_id
        }
    )
    return all([user.get(dep + "Access") for dep in departments])


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
