import os, json, time
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# তোমার দেওয়া মডেলগুলো (যেগুলো আসলে অ্যাক্সেস আছে)
MODEL_LIST = [
    'gemini-3.5-flash-lite',   # তুমি বলেছ এটা আছে
    'gemini-3.6-flash',
    'gemini-3.1-pro',
    # যদি এগুলো ফেইল করে, তাহলে আরও কিছু কমন ফ্রি মডেল ট্রাই করতে পারো
    'gemini-2.0-flash',        # ব্যাকআপ
    'gemini-1.5-flash-lite',   # পুরনো কিন্তু ফ্রি
    'gemini-1.5-flash',
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
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].strip()
            parsed = json.loads(text)
            required = ['trend', 'confidence', 'risk', 'target', 'stop_loss', 'summary']
            for r in required:
                if r not in parsed:
                    raise ValueError(f"Missing key {r}")
            return parsed
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}")
            time.sleep(1)
            continue
    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return {
        'trend': 'Neutral',
        'confidence': analysis_data['confidence'],
        'risk': analysis_data['risk'],
        'target': analysis_data['target'],
        'stop_loss': analysis_data['stoploss'],
        'summary': 'AI analysis temporarily unavailable. Please check model availability.'
    }
