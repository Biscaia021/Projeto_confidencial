import json
import os
import urllib.request
import urllib.error

def handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Content-Type": "application/json"
    }

    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    try:
        body = json.loads(event.get("body", "{}")) if event.get("body") else {}
        user_message = body.get("message", body.get("prompt", "Olá! Quem é Rafael Carvalho?"))
        api_key = body.get("apiKey") or os.environ.get("OPENROUTER_API_KEY", "")

        model = body.get("model", "google/gemma-2-9b-it:free")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é o assistente virtual IA do portfólio de Rafael Carvalho (Data Scientist & Engenheiro de IA). "
                        "Responda de forma cortês, profissional e precisa sobre as experiências, habilidades em IA (CNN, NLP, LLMs, PyTorch, Python, AWS, Docker) "
                        "e projetos desenvolvidos por Rafael."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }

        req_headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Biscaia021",
            "X-Title": "Rafael Portfolio AI Assistant"
        }

        if api_key:
            req_headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=req_headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            choices = res_data.get("choices", [])
            reply = choices[0]["message"]["content"] if choices else "Sem resposta do modelo."
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "reply": reply,
                    "model": model
                })
            }

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if e.fp else str(e)
        return {
            "statusCode": e.code,
            "headers": headers,
            "body": json.dumps({"success": False, "error": f"OpenRouter HTTP Error ({e.code}): {err_msg}"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"success": False, "error": f"Internal Server Error: {str(e)}"})
        }
