import httpx

FASTAPI_URL = "http://192.168.199.38:8000/ask"

async def ask_faq_api(question: str):
    payload = {"question": question}
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL, json=payload, timeout=10.0)
        response.raise_for_status()  # Raise exception on HTTP error
        data = response.json()
        return data["matched_question"], data["answer"]