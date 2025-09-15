# wolfram_module.py
import requests
import database  # dùng chung DB module bạn đã có

WOLFRAM_APP_ID = "YOUR_APP_ID"

def query_wolfram(question: str):
    """Query Wolfram API"""
    url = "https://api.wolframalpha.com/v2/query"
    params = {
        "input": question,
        "appid": WOLFRAM_APP_ID,
        "output": "JSON",
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        try:
            pods = data["queryresult"]["pods"]
            for pod in pods:
                if pod["title"].lower() in ["result", "definite integral", "solution", "value"]:
                    return pod["subpods"][0]["plaintext"]
            # fallback: lấy cái đầu tiên có text
            return pods[0]["subpods"][0]["plaintext"]
        except Exception:
            return None
    return None

def get_or_cache_answer(problem_id: int, variant_text: str) -> str:
    """Check DB cache, nếu chưa có thì query Wolfram và lưu lại"""
    # kiểm tra DB
    answer = database.get_answer(problem_id, variant_text)
    if answer:
        return answer
    
    # chưa có → query Wolfram
    answer = query_wolfram(variant_text)
    if answer:
        database.save_answer(problem_id, variant_text, answer)
    return answer
