import json
from io import BytesIO
from typing import Any
from PIL import Image
from app.config import get_settings

try:
    from google import genai
except ImportError:
    genai = None

class GeminiService:
    def __init__(self):
        s=get_settings(); self.enabled=bool(s.gemini_api_key and genai); self.model=s.gemini_model
        self.client=genai.Client(api_key=s.gemini_api_key) if self.enabled else None

    def _prompt(self, planner: str, data: dict[str,Any]) -> str:
        return f"""You are PocketSmart AI, a budget recommendation assistant. Planner: {planner}.\nUser input JSON: {json.dumps(data)}\nReturn ONLY valid JSON with keys: summary (string), allocation (object of category to number), recommendations (array). Each recommendation must contain name, category, platform, estimated_price, quantity, subtotal, reason, link. Keep total recommendation spend <= budget. Do not claim live availability. Use platform names from Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO or Local Vendor. Links may be search links. Be practical and concise."""

    def generate(self, planner: str, data: dict[str,Any], image_bytes: bytes|None=None, mime_type: str|None=None):
        if not self.enabled: return None
        try:
            contents=[self._prompt(planner,data)]
            if image_bytes:
                img=Image.open(BytesIO(image_bytes)); contents.append(img)
                contents[0] += "\nAn outfit image is attached. Consider visible colors, formality, and style; do not infer sensitive personal attributes."
            response=self.client.models.generate_content(model=self.model, contents=contents)
            raw=(response.text or "").strip()
            if raw.startswith("```"): raw=raw.strip("`"); raw=raw.replace("json\n", "", 1)
            return json.loads(raw)
        except Exception:
            return None
