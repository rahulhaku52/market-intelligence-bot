import os
import json
import time
import re
from google import genai
from jinja2 import Template
from src.utils.logger import logger

def generate_ai_explanation(analysis_data: dict) -> str:
    """
    Gemini AI Explanation Engine.
    Strictly generates natural language explanation of Python's deterministic setup.
    If Gemini fails or is unavailable, falls back to a Python deterministic explanation string.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Using Python deterministic explanation fallback.")
        return generate_python_fallback_explanation(analysis_data)
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            f"You are a senior Indian stock market analyst. Explain why the following setup for {analysis_data['ticker']} is noteworthy.\n"
            f"Data: Price={analysis_data['price']}, Trend={analysis_data['trend']}, Setup Score={analysis_data['score']}, "
            f"Sector={analysis_data.get('sector')}, Confidence={analysis_data['score']}%, Risk={analysis_data['risk']}.\n"
            f"Write a concise 2-sentence rationale highlighting the key technical and market driver."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}. Falling back to Python explanation.")
        
    return generate_python_fallback_explanation(analysis_data)

def generate_python_fallback_explanation(analysis_data: dict) -> str:
    ticker = analysis_data.get('ticker', '')
    trend = analysis_data.get('trend', 'NEUTRAL')
    score = analysis_data.get('score', 50)
    sector = analysis_data.get('sector', 'General')
    
    return (
        f"Technical structure for {ticker} exhibits a {trend.lower()} setup with a confluence score of {score}/100. "
        f"The setup is supported by multi-timeframe alignment in the {sector} sector."
    )
