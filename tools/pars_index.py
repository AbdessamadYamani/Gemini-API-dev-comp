from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
import os
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-JdxvuqrHtfgwMcFFNMEfFgYPjZ8Aclt8iczRigbpkCeiIXUI"


def Llama_parse(query:str):
    parser = LlamaParse()

    documents = LlamaParse(
parsing_instruction=query    ,                result_type="markdown"         
).load_data(r"C:\Users\user\Documents\Gemini API dev comp\sources\cources\user_form.txt")
    return(documents)
