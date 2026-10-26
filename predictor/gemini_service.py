"""
Gemini Multilingual Translation Service for ArecaLens.
Provides real-time, accurate agricultural translations for any language using Google Gemini API.
Includes a persistent disk cache to minimize latency and API calls.
"""

import json
import logging
import os
import urllib.request
import urllib.error
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

CACHE_FILE = Path(settings.BASE_DIR) / 'predictor' / 'data' / 'translation_cache.json'


def get_gemini_api_key():
    """Retrieves the Gemini API Key from settings, environment, or .env file."""
    key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    if not key:
        env_path = Path(settings.BASE_DIR) / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GEMINI_API_KEY='):
                        key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        os.environ['GEMINI_API_KEY'] = key
                        break
    return key


def save_gemini_api_key(new_key):
    """Safely saves a new Gemini API Key to .env and updates the active runtime environment."""
    new_key = new_key.strip()
    if not new_key:
        return False, "Empty API key provided."

    env_path = Path(settings.BASE_DIR) / '.env'
    lines = []
    found = False

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY='):
                    lines.append(f"GEMINI_API_KEY={new_key}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"GEMINI_API_KEY={new_key}\n")

    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    os.environ['GEMINI_API_KEY'] = new_key
    if hasattr(settings, 'GEMINI_API_KEY'):
        settings.GEMINI_API_KEY = new_key

    return True, "API Key saved successfully."


def load_translation_cache():
    """Loads the cached translations from disk."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Could not read translation cache: %s", e)
    return {}


def save_translation_cache(cache_data):
    """Saves translations to disk cache."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Failed to save translation cache: %s", e)


def translate_keys_with_gemini(keys_dict, target_lang, lang_name=""):
    """
    Translates a dictionary of UI keys { key_name: english_text } into target_lang using Gemini.
    Uses cached translations wherever possible to avoid redundant API requests.
    """
    cache = load_translation_cache()
    if target_lang not in cache:
        cache[target_lang] = {}

    target_cache = cache[target_lang]
    missing_keys = {k: v for k, v in keys_dict.items() if k not in target_cache}

    # If all requested keys are already cached, return immediately
    if not missing_keys:
        return {k: target_cache[k] for k in keys_dict if k in target_cache}

    api_key = get_gemini_api_key()
    if not api_key:
        logger.info("No Gemini API key available; returning available cached keys or English fallbacks.")
        # Return whatever is cached, or original English for missing
        result = {}
        for k, v in keys_dict.items():
            result[k] = target_cache.get(k, v)
        return result

    # Batch translate missing keys using Gemini
    lang_display = lang_name if lang_name else target_lang
    items_to_translate = list(missing_keys.items())

    # Chunk into manageable batches of 40 keys
    chunk_size = 40
    for i in range(0, len(items_to_translate), chunk_size):
        chunk = dict(items_to_translate[i:i + chunk_size])
        translated_chunk = _call_gemini_for_translations(chunk, target_lang, lang_display, api_key)
        target_cache.update(translated_chunk)

    # Persist updated cache
    cache[target_lang] = target_cache
    save_translation_cache(cache)

    # Return full translation set for the requested keys
    return {k: target_cache.get(k, keys_dict[k]) for k in keys_dict}


def _call_gemini_for_translations(chunk_dict, target_lang, lang_name, api_key):
    """Internal helper to invoke Google Gemini REST API."""
    prompt = (
        f"You are an expert multilingual translator and agricultural agronomist for ArecaLens "
        f"(an arecanut palm disease diagnostic platform).\n"
        f"Translate the following JSON key-value pairs into {lang_name} ({target_lang}).\n"
        f"Instructions:\n"
        f"1. Maintain cultural and technical agronomic accuracy for arecanut (adike/supari/betel nut) growers.\n"
        f"2. Keep technical acronyms intact where standard (e.g. ResNet-50, Grad-CAM, ICAR-CPCRI, XAI, RGB, JPG, 224x224).\n"
        f"3. Preserve HTML tags or entities like <strong>, <em>, ➔, ◂, ⚡, 🍃 exactly as they are.\n"
        f"4. Return ONLY a valid JSON object mapping the exact same keys to their translated values.\n\n"
        f"JSON to translate:\n"
        f"{json.dumps(chunk_dict, ensure_ascii=False)}"
    )

    models_to_try = ["gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-flash-latest"]
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                raw_text = resp_data['candidates'][0]['content']['parts'][0]['text']
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    return parsed
        except urllib.error.HTTPError as http_err:
            logger.warning("Gemini model %s returned HTTP %s", model, http_err.code)
            continue
        except Exception as err:
            logger.warning("Gemini model %s failed: %s", model, err)
            continue

    # Fallback to English if API failed
    return chunk_dict
