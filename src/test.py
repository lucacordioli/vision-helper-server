import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


question = "How many apple revnue in the second quarter of 2024?"
system_message = ""

urls = [
    "https://www.apple.com/newsroom/2024/05/apple-reports-second-quarter-results/"
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=600, chunk_overlap=100)
doc_splits = text_splitter.split_documents(docs_list)

huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

chroma_client = chromadb.Client()
# client = chromadb.PersistentClient(path="/path/to/save/to")
collection = chroma_client.create_collection(name="my_collection", embedding_function=huggingface_ef)

collection.add(
    documents=[doc.page_content for doc in doc_splits],
    metadatas=[doc.metadata for doc in doc_splits],
    ids=[f"id_{doc}" for doc in range(len(doc_splits))]
)

results = collection.query(
    query_texts=[question],
    n_results=3,
    include=["documents"]
)

context = ""
for doc in results["documents"]:
    context += "\n\n".join(doc)


print('\n\n\n')

llm = ChatOllama(model="llama3:8b", temperature=0, max_tokens=2048,
                 stop=["<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>", "<|reserved_special_token"])

prompt = PromptTemplate(
    template="""<|begin_of_text|>
      <|start_header_id|>system<|end_header_id|>You are a question-answer task assistant. Use the following portion of the context to answer the question. If you do not know the answer, simply answer that you do not know the answer. Use a maximum of 3 sentences to answer concisely.<|eot_id|>
      <|start_header_id|>user<|end_header_id|>
      Question: {question}
      Context: {context}
      Answer: <|eot_id|>
      <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["system_message", "question", "context"],
)

chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"question": question, "system_message": system_message, "context": context}):
    print(chunk, end="", flush=True)

