import os
import json
import re
import logging
from typing import Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _clean_json_response(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start:end + 1]
    return raw


def call_gemini(prompt: str, retries: int = 3) -> dict[str, Any]:
    last_error = None
    for attempt in range(retries):
        try:
            logger.info(f"Groq API call attempt {attempt + 1}")
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Indian financial advisor AI. Always respond with valid JSON only. No markdown, no prose, no code fences. Start directly with { and end with }."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            logger.info(f"Groq response length: {len(raw)}")
            cleaned = _clean_json_response(raw)
            parsed = json.loads(cleaned)
            logger.info("Groq response parsed successfully")
            return {"success": True, "data": parsed}
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed attempt {attempt + 1}: {e}")
            last_error = str(e)
        except Exception as e:
            logger.error(f"Groq API error attempt {attempt + 1}: {e}")
            last_error = str(e)
    return {"success": False, "error": last_error, "data": None}