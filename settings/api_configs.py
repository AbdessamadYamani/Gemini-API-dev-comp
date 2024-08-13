from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from llama_index.embeddings.jinaai import JinaEmbedding
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_community.embeddings import JinaEmbeddings


jinaai_api_key = "jina_378f35a379164692bfb3d4c112c69e81pNkAu7HGviV82ArdlNwG14pANoa6"
os.environ["JINAAI_API_KEY"] = jinaai_api_key
# Configure the API with your API key

openai_api_key = "AIzaSyAVVNPa6KxX9N2PUylNkkYqr51MFdweVOo"
# llx-KrqM6oxe1lkv1njfSKJMC17WU4AInakXku1eTsQ8deBVsxep
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=openai_api_key)
embedding_function = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004",google_api_key=openai_api_key)
# embedding_function = JinaEmbeddings(
#     jina_api_key="jina_378f35a379164692bfb3d4c112c69e81pNkAu7HGviV82ArdlNwG14pANoa6", model_name="jina-embeddings-v2-base-en"
# )

directory_RAG_path=r".\sources"
tuto_path=r"C:\Users\user\Documents\Gemini API dev comp\sources\cources"