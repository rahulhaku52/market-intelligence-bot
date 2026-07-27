import os
import json
from google import genai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_exponential

# Create a client using the new API
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def load_prompt(template_path, **kwargs):
    with open(template_path, 'r') as f:
        tmpl = Template(f.read())
    return tmpl.render(**kwargs)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_structured_analysis(analysis_data):
    prompt = load_prompt('prompts/explain.txt', **analysis_data)
    response = client.models.generate_content(
        model='gemini-2.5-flash',  # or gemini-2.5-pro if you have access
        contents=prompt
    )
    try:
        text = response.text
        # Extract JSON from code block if present
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
        # Fallback
        return {
            'trend': 'Neutral',
            'confidence': analysis_data['confidence'],
            'risk': analysis_data['risk'],
            'target': analysis_data['target'],
            'stop_loss': analysis_data['stoploss'],
            'summary': response.text[:300]
        }
