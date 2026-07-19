import os

# USER_AGENT wali warning khatam karne ke liye:
os.environ["USER_AGENT"] = "RestaurantChatbot/1.0"

from langchain_community.document_loaders import WebBaseLoader
# Text splitter ki naye package wali import:
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

print("Dependencies load ho gayin. Website se data fetch ho raha hai...")

# 1. Data Load Karna (Yahan kisi bhi restaurant/menu website ka link aayega)
# Abhi ke liye hum ek example page use kar rahe hain:
url = "https://themonal.com/our-menus/" 
loader = WebBaseLoader(url)
web_data = loader.load()

print("Data fetch ho gaya. Chunks ban rahe hain...")

# 2. Data ko Chunks mein Split Karna
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
documents = text_splitter.split_documents(web_data)

print("Chunks ban gaye. Vector Embeddings tayar ho rahi hain (is mein thora time lag sakta hai)...")

# 3. Vector Embeddings banana aur ChromaDB mein save karna
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma.from_documents(documents, embeddings)

print("Database tayar hai! Ab hum testing kar rahe hain...\n")
print("-" * 50)

# 4. Data Retrieve karna (Testing ke liye)
retriever = vector_db.as_retriever(search_kwargs={"k": 2}) # Sirf top 2 relevant chunks laye ga
query = "What dishes are available in the menu?"
query = "What dishes are available in the menu?"
relevant_docs = retriever.invoke(query)

print(f"User Query: {query}\n")

if relevant_docs:
    print("AI ke liye Retrieved Data:\n")
    print(relevant_docs[0].page_content)
else:
    print("Koi relevant data nahi mila.")

print("-" * 50)
print("\nPipeline successfully chal gayi hai!")