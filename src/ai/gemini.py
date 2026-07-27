import os, json, time, re
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

MODEL_LIST = [
    'gemini-3.5-flash-lite',
    'gemini-3.6-flash',
]

def load_prompt(template_path, **kwargs):
    with open(template_path, 'r') as f:
        tmpl = Template(f.read())
    return tmpl.render(**kwargs)

def _clean_json(text):
    """Try to extract and fix common JSON issues from model output."""
    # Remove markdown code fences
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].strip()
    # Remove trailing commas before closing brackets
    text = re.sub(r',\s*(?=[}\]])', '', text)
    # Try to fix unquoted keys (simple)
    # But better to let json.loads handle, just return cleaned text
    return text

def generate_structured_analysis(analysis_data):
    prompt = load_prompt('prompts/explain.txt', **analysis_data)
    last_error = None
    for model_name in MODEL_LIST:
        try:
            logger.info(f"Trying Gemini model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw = response.text
            cleaned = _clean_json(raw)
            parsed = json.loads(cleaned)
            required = [
                'trend', 'bias', 'timeframe', 'entry_zone',
                'tp_short', 'sl_short', 'tp_mid', 'sl_mid',
                'tp_long', 'sl_long', 'invalidation', 'reasons',
                'scenarios', 'confidence', 'risk', 'data_freshness', 'status'
            ]
            for key in required:
                if key not in parsed:
                    raise ValueError(f"Missing key: {key}")
            parsed['data_freshness'] = parsed.get('data_freshness', 'N/A')
            return parsed
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}")
            time.sleep(1)  # avoid rate limits
            continue

    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return None
