import os, json, time
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# Use the models you have access to: 3.5 Flash-Lite (fastest), 3.6 Flash (all-around), 3.1 Pro (advanced) - though 3.1 Pro may not support generateContent yet, we'll try.
MODEL_LIST = [
    'gemini-3.5-flash-lite',
    'gemini-3.6-flash',
    # 'gemini-3.1-pro',  # may return 404, so can skip or keep but handle
]

def load_prompt(template_path, **kwargs):
    with open(template_path, 'r') as f:
        tmpl = Template(f.read())
    return tmpl.render(**kwargs)

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
            text = response.text
            # Extract JSON from markdown code block if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].strip()
            parsed = json.loads(text)
            # Required keys for god-level report
            required = [
                'trend', 'bias', 'timeframe', 'entry_zone',
                'tp_short', 'sl_short', 'tp_mid', 'sl_mid',
                'tp_long', 'sl_long', 'invalidation', 'reasons',
                'scenarios', 'confidence', 'risk', 'data_freshness', 'status'
            ]
            for key in required:
                if key not in parsed:
                    raise ValueError(f"Missing key: {key}")
            # Add default data_freshness if missing
            parsed['data_freshness'] = parsed.get('data_freshness', 'N/A')
            return parsed
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}")
            time.sleep(1)  # avoid rate limits
            continue

    # If all models fail, return None (we will not post)
    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return None  # signal that we couldn't get analysis
