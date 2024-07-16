import ollama
from typing import List, Dict, AsyncGenerator

class OllamaService:
    def __init__(self, host: str, port: str):
        self.client = ollama.AsyncClient(host=f"{host}:{port}")

    async def get_model_response(self, model_name: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat(
                model=model_name,
                messages=messages,
                stream=True
            )
            full_response = ""
            async for chunk in stream:
                if isinstance(chunk, dict) and 'message' in chunk:
                    content = chunk['message'].get('content', '')
                    full_response += content
                    yield full_response
                else:
                    print(f"Unexpected chunk format: {chunk}")
        except Exception as e:
            yield f"Error getting response from model: {str(e)}"

    async def get_available_models(self) -> List[str]:
        try:
            models = await self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    async def get_model_info(self, model_name: str) -> Dict[str, str]:
        try:
            model_info = await self.client.show(model_name)
            return model_info
        except Exception as e:
            print(f"Error fetching model info for {model_name}: {str(e)}")
            return {}
