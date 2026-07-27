import os, json, time
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def load_prompt(template_path, **kwargs):
    with open(template_path, 'r') as f:
        tmpl = Template(f.read())
    return tmpl.render(**kwargs)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def generate_structured_analysis(analysis_data):
    prompt = load_prompt('prompts/explain.txt', **analysis_data)
    try:
        # Use gemini-2.0-flash (free, available) — NOT the deprecated 1.5 flash
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        text = response.text
        # Extract JSON from possible markdown code block
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
        logger.warning(f"Gemini failed, using fallback: {e}")
        return {
            'trend': 'Neutral',
            'confidence': analysis_data['confidence'],
            'risk': analysis_data['risk'],
            'target': analysis_data['target'],
            'stop_loss': analysis_data['stoploss'],
            'summary': 'AI analysis temporarily unavailable.'
        }
