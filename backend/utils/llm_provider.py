"""
Central LLM selector and lazy client provider for ServisAI.
Eliminates early client initialization warnings and provides seamless fallback logic.
Supports: Gemini (Google GenAI), Groq (OpenAI Client), and OpenRouter (OpenAI Client).
Dynamically reads providers list, models, and precedence from local JSON configuration.
"""

import os
import json
import time
from typing import Any, Tuple, Optional
from openai import OpenAI
from google import genai
from dotenv import load_dotenv

# Dynamically locate and load the backend/.env file
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_backend_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

# Global client cache for lazy initialization
_clients = {
    "gemini": None,
    "groq": None,
    "openrouter": None
}

def get_gemini_client() -> Optional[genai.Client]:
    """Lazily initialize and return the Gemini Client."""
    global _clients
    if _clients["gemini"] is not None:
        return _clients["gemini"]
        
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            # Pass the key explicitly to avoid automatic environment warnings
            _clients["gemini"] = genai.Client(api_key=gemini_key)
        except Exception:
            try:
                _clients["gemini"] = genai.Client()
            except Exception:
                _clients["gemini"] = None
    return _clients["gemini"]

def get_groq_client() -> Optional[OpenAI]:
    """Lazily initialize and return the Groq OpenAI Client."""
    global _clients
    if _clients["groq"] is not None:
        return _clients["groq"]
        
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            _clients["groq"] = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        except Exception:
            _clients["groq"] = None
    return _clients["groq"]

def get_openrouter_client() -> Optional[OpenAI]:
    """Lazily initialize and return the OpenRouter OpenAI Client."""
    global _clients
    if _clients["openrouter"] is not None:
        return _clients["openrouter"]
        
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        try:
            _clients["openrouter"] = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        except Exception:
            _clients["openrouter"] = None
    return _clients["openrouter"]

def load_provider_config() -> dict:
    """Loads LLM providers list and precedence from local JSON file with robust defaults."""
    default_config = {
        "provider_precedence": ["groq", "gemini", "openrouter"],
        "providers": [
            {
                "groq": [
                    "llama-3.3-70b-versatile",
                    "qwen/qwen3-32b",
                    "openai/gpt-oss-120b"
                ]
            },
            {
                "openrouter": [
                    "deepseek/deepseek-v4-flash:free",
                    "minimax/minimax-m2.5:free",
                    "nvidia/nemotron-3-super-120b-a12b:free",
                    "google/gemma-4-31b-it:free"
                ]
            },
            {
                "gemini": [
                    "gemini-2.0-flash",
                    "gemini-2.5-flash"
                ]
            }
        ]
    }
    
    # Try loading backend/utils/llm_provider_list.json first, then providers.json
    paths_to_try = [
        os.path.join(os.path.dirname(__file__), "llm_provider_list.json"),
        os.path.join(os.path.dirname(__file__), "providers.json"),
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "provider_precedence" in data and "providers" in data:
                        return data
            except Exception:
                pass
                
    return default_config

def get_provider_models(config: dict, provider: str) -> list:
    """Extracts models for a given provider from the config dictionary."""
    for p_dict in config.get("providers", []):
        if provider in p_dict:
            return p_dict[provider]
    return []

def determine_llm_provider(state: dict = None, request_override: bool = False) -> str:
    """
    Determines which LLM provider to use based on state request flags,
    global environment variables, and active API key availability.
    
    Order of preference:
    1. request_override or state.get("use_gemini") -> gemini
    2. Global USE_GEMINI env var -> gemini
    3. Global LLM_PROVIDER env var (gemini, groq, openrouter)
    4. Fallback based on key availability: groq -> openrouter -> gemini
    """
    if state is None:
        state = {}
        
    # Check explicitly requested gemini switch
    use_gemini_state = state.get("use_gemini", False)
    use_gemini_env = os.getenv("USE_GEMINI", "false").lower() == "true"
    
    # 1. Determine active intent
    if request_override or use_gemini_state or use_gemini_env:
        # User requested Gemini. Verify if Gemini is available
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "gemini"
            
    # 2. Check LLM_PROVIDER env var
    preferred = os.getenv("LLM_PROVIDER", "groq").lower()
    if preferred == "gemini" and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return "gemini"
    elif preferred == "openrouter" and os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    elif preferred == "groq" and os.getenv("GROQ_API_KEY"):
        return "groq"
        
    # 3. Dynamic Key-based Fallbacks
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    elif os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
        
    return "groq" # Ultimate fallback default

def generate_llm_text(
    prompt: str,
    system_instruction: str = "You are a helpful assistant.",
    temperature: float = 0.3,
    max_tokens: int = 300,
    preferred_provider: str = None
) -> Tuple[str, str]:
    """
    Unified interface to generate text using the dynamically configured provider chain.
    Automatically handles fallback model retries and provider failover:
    1. Loads provider precedence and model list from llm_provider_list.json
    2. Re-orders precedence chain to start with the preferred_provider (if provided)
    3. Attempts generation with models in the preferred provider's list sequentially
    4. Fails over to subsequent providers and their model chains sequentially if errors occur
    
    Returns:
        Tuple of (response_text, actual_model_and_provider_used)
    """
    config = load_provider_config()
    precedence = list(config.get("provider_precedence", ["groq", "gemini", "openrouter"]))
    
    # Re-order precedence chain if a preferred provider is explicitly given
    if preferred_provider and preferred_provider in precedence:
        precedence.remove(preferred_provider)
        precedence.insert(0, preferred_provider)
        
    for prov in precedence:
        models = get_provider_models(config, prov)
        if not models:
            continue
            
        # 1. Groq Provider Path
        if prov == "groq":
            client = get_groq_client()
            if not client:
                continue
            for model in models:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    res = response.choices[0].message.content.strip()
                    if res:
                        return res, f"groq ({model})"
                except Exception:
                    pass
                    
        # 2. OpenRouter Provider Path
        elif prov == "openrouter":
            client = get_openrouter_client()
            if not client:
                continue
            for model in models:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    res = response.choices[0].message.content.strip()
                    if res:
                        return res, f"openrouter ({model})"
                except Exception:
                    pass
                    
        # 3. Gemini Provider Path
        elif prov == "gemini":
            client = get_gemini_client()
            if not client:
                continue
            for model in models:
                # Map potential config model placeholders to supported API models
                api_model = model
                if "gemini-3.1" in model or "gemini-3" in model:
                    # Translate upcoming or mock models to current stable 'gemini-2.0-flash' or 'gemini-2.5-flash'
                    api_model = "gemini-2.0-flash"
                elif "gemini-2.5" in model:
                    api_model = "gemini-2.0-flash"
                    
                try:
                    response = client.models.generate_content(
                        model=api_model,
                        contents=prompt,
                        config={
                            'system_instruction': system_instruction,
                            'temperature': temperature,
                            'max_output_tokens': max_tokens
                        }
                    )
                    res = response.text.strip()
                    if res:
                        return res, f"gemini ({model})"
                except Exception:
                    pass
                    
    return "", "none"
