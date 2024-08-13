from langchain.tools import tool
import requests
#f110d983-481c-4942-b1cc-3e581f4dd4ab_workspace     /    Access token : aJ2rJvt6Wlfrwg0zrSssQRBCY5rSHAsu
class RAGGradient:
    
    # gradient = Gradient()

    @tool("RAG collector tool")
    def RAGCollector(query:str):
        """Charge et traite le contenu des documents"""
        # value=DocKBCClass.load_content_from_all_types()
        # gradient = Gradient()
        # result = gradient.answer(
        #     question=query,
        #     source={
        #         "type": "document",
        #         "value": value,
        #     },
        # )
        # return result

        url = "https://api.gradient.ai/api/blocks/answer"

        payloads = {
            "question": query,
            "source": {
                "collectionId": "876247a2-9ff2-4694-b89d-fac43267c95f_rag_config",
                "type": "rag"
            }
        }
        headerss = {
            "accept": "application/json",
            "x-gradient-workspace-id": "f110d983-481c-4942-b1cc-3e581f4dd4ab_workspace",
            "content-type": "application/json",
            "authorization": "Bearer uh0ACBGbChwlP8zDtZanmKTJhxWmnn6h"
        }

        response_r = requests.post(url, json=payloads, headers=headerss)

        # url = "https://api.gradient.ai/api/embeddings/bge-large"

        # payload = { "inputs": [{ "input": response_r.text }] }
        # headers = {
        #     "accept": "application/json",
        #     "x-gradient-workspace-id": "5ee426a1-de00-4986-b460-20e098900be0_workspace",
        #     "content-type": "application/json",
        #     "authorization": "Bearer uh0ACBGbChwlP8zDtZanmKTJhxWmnn6h"
        # }

        # response = requests.post(url, json=payload, headers=headers)

        return response_r.content
	

# print(RAGGradient.RAGCollector("Tell me about Abdessamad")	)