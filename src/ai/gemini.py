import os, json, time
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

MODEL_LIST = [
    'gemini-2.0-flash',          # free tier (but rate-limited)
    'gemini-1.5-flash',          # deprecated but may work
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
            # Required keys matching the prompt
            required = ['trend', 'confidence', 'risk',
                        'target_short_term', 'stop_loss_short_term',
                        'target_long_term', 'stop_loss_long_term',
                        'entry_zone', 'exit_signal', 'summary']
            for r in required:
                if r not in parsed:
                    raise ValueError(f"Missing key {r}")
            return parsed
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}")
            time.sleep(1)  # small delay before next model
            continue

    # All models failed, use fallback using values from analysis_data
    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return {
        'trend': 'Neutral',
        'confidence': analysis_data.get('confidence', 50),
        'risk': analysis_data.get('risk', 'Medium'),
        'target_short_term': analysis_data.get('target', 'N/A'),
        'stop_loss_short_term': analysis_data.get('stoploss', 'N/A'),
        'target_long_term': analysis_data.get('target', 'N/A'),
        'stop_loss_long_term': analysis_data.get('stoploss', 'N/A'),
        'entry_zone': 'N/A',
        'exit_signal': 'N/A',
        'summary': 'AI analysis temporarily unavailable.'
    }
