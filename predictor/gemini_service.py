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


# =========================================================================
# PRELOADED AGRONOMY AI KNOWLEDGE BASE & CHATBOT SERVICE
# =========================================================================

PRELOADED_AGRONOMY_KB = {
    "bordeaux": {
        "keywords": ["bordeaux", "mixture", "copper sulphate", "lime", "ಬೋರ್ಡೋ", "ದ್ರಾವಣ", "ಕಬ್ಬಿಣ", "छिड़काव", "ബോർഡോ", "തുരിശ്"],
        "replies": {
            "en": """### 1% Bordeaux Mixture Preparation Protocol (ICAR-CPCRI Standard)
1. **Ingredients (for 100 Litres):**
   - 1 kg Copper Sulphate (Blue Vitriol / Cupric Sulphate)
   - 1 kg Fresh Slaked Lime (Calcium Hydroxide)
   - 100 Litres clean water
2. **Step-by-step Mixing:**
   - Dissolve 1 kg copper sulphate in 50 litres of water in a wooden, plastic, or earthen container (never metal).
   - Slake 1 kg lime in a separate container with 50 litres of water to form milk of lime.
   - Slowly pour the copper sulphate solution into the milk of lime while stirring continuously.
3. **Neutrality Test:**
   - Dip a clean, shiny iron blade/knife into the mixture for 1 minute.
   - If a reddish copper coating appears, the solution is acidic: add more lime water until knife remains clean.
4. **Application Timing:**
   - **1st Spray:** Late May or early June, immediately before the onset of the South-West monsoon.
   - **2nd Spray:** 40 to 45 days later during a break in rains.
   - Add resin-soda or commercial adhesive (wetting agent) to prevent rain wash-off.""",
            "kn": """### ೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ತಯಾರಿಸುವ ಅಧಿಕೃತ ವಿಧಾನ (ICAR-CPCRI ಶಿಫಾರಸು)
೧. **ಬೇಕಾಗುವ ಸಾಮಗ್ರಿಗಳು (೧೦೦ ಲೀಟರ್ ದ್ರಾವಣಕ್ಕೆ):**
   - ೧ ಕೆ.ಜಿ ಮೈಲುತುತ್ತ (ಕಾಪರ್ ಸಲ್ಫೇಟ್)
   - ೧ ಕೆ.ಜಿ ಸುಣ್ಣ (ತಾಜಾ ಕಲ್ನಾರು ಸುಣ್ಣ)
   - ೧೦೦ ಲೀಟರ್ ಶುದ್ಧ ನೀರು
೨. **ತಯಾರಿಸುವ ಕ್ರಮ:**
   - ೫೦ ಲೀಟರ್ ನೀರಿನಲ್ಲಿ ೧ ಕೆ.ಜಿ ಮೈಲುತುತ್ತನ್ನು ಪ್ಲಾಸ್ಟಿಕ್ ಅಥವಾ ಮಣ್ಣಿನ ಪಾತ್ರೆಯಲ್ಲಿ ಕರಗಿಸಿ (ಕಬ್ಬಿಣದ ಪಾತ್ರೆ ಬಳಸಬೇಡಿ).
   - ಪ್ರತ್ಯೇಕ ಪಾತ್ರೆಯಲ್ಲಿ ೫೦ ಲೀಟರ್ ನೀರಿಗೆ ೧ ಕೆ.ಜಿ ಸುಣ್ಣ ಬೆರೆಸಿ ಸುಣ್ಣದ ತಿಳಿ ದ್ರಾವಣ ತಯಾರಿಸಿ.
   - ಮೈಲುತುತ್ತಿನ ದ್ರಾವಣವನ್ನು ನಿಧಾನವಾಗಿ ಸುಣ್ಣದ ತಿಳಿನೀರಿಗೆ ಸುರಿಯುತ್ತಾ ಕೋಲಿನಿಂದ ಚೆನ್ನಾಗಿ ತಿರುಗಿಸಿ.
೩. **ಪರೀಕ್ಷೆ (ತಟಸ್ಥ ಪರೀಕ್ಷೆ):**
   - ಸ್ವಚ್ಛವಾದ ಕಬ್ಬಿಣದ ಚಾಕುವನ್ನು ದ್ರಾವಣದಲ್ಲಿ ೧ ನಿಮಿಷ ಮುಳುಗಿಸಿ ನೋಡಿ.
   - ಚಾಕುವಿನ ಮೇಲೆ ಕೆಂಪು ಕಲೆ ಕುಳಿತರೆ ದ್ರಾವಣ ಆಮ್ಲೀಯವಾಗಿದೆ ಎಂದರ್ಥ; ಕಲೆ ಬರದೇ ಇರುವವರೆಗೆ ಸ್ವಲ್ಪ ಸುಣ್ಣದ ನೀರನ್ನು ಬೆರೆಸಿ.
೪. **ಸಿಂಪಡಣಾ ಸಮಯ:**
   - **ಮೊದಲ ಸಿಂಪಡಣೆ:** ಮುಂಗಾರು ಮಳೆ ಪ್ರಾರಂಭವಾಗುವ ಮುನ್ನ (ಮೇ ಅಂತ್ಯ ಅಥವಾ ಜೂನ್ ಮೊದಲ ವಾರ).
   - **ಎರಡನೇ ಸಿಂಪಡಣೆ:** ಮಳೆಗಾಲದ ಮಧ್ಯೆ ಮಳೆ ಬಿಡುವು ನೀಡಿದಾಗ (೪೦-೪೫ ದಿನಗಳ ನಂತರ).""",
            "hi": """### 1% बोर्डो मिश्रण तैयार करने की प्रामाणिक विधि (ICAR-CPCRI)
1. **आवश्यक सामग्री (100 लीटर के लिए):**
   - 1 किग्रा कॉपर सल्फेट (नीला थोथा)
   - 1 किग्रा बुझा हुआ चूना
   - 100 लीटर साफ पानी
2. **बनाने की विधि:**
   - 50 लीटर पानी में 1 किग्रा नीला थोथा प्लास्टिक या मिट्टी के बर्तन में घोलें।
   - दूसरे बर्तन में 50 लीटर पानी में 1 किग्रा चूना घोलकर चूने का पानी तैयार करें।
   - नीले थोथे के घोल को धीरे-धीरे चूने के घोल में मिलाते हुए हिलाएँ।
3. **परीक्षण:**
   - साफ लोहे का चाकू घोल में 1 मिनट डुबोएँ। यदि लाल परत चढ़े तो और चूना मिलाएँ जब तक चाकू साफ न निकले।
4. **छिड़काव का समय:**
   - मानसून से ठीक पहले (मई अंत या जून प्रथम सप्ताह) और दूसरा छिड़काव 40-45 दिन बाद।""",
            "ml": """### 1% ബോർഡോ മിശ്രിതം തയ്യാറാക്കുന്ന വിധം (ICAR-CPCRI)
1. **ആവശ്യമായ ചേരുവകൾ (100 ലിറ്ററിന്):**
   - 1 കിലോഗ്രാം തുരിശ് (Copper Sulphate)
   - 1 കിലോഗ്രാം നീറ്റുകക്ക (Slaked Lime)
   - 100 ലിറ്റർ ശുദ്ധജലം
2. **മിക്സിങ് രീതി:**
   - 50 ലിറ്റർ വെള്ളത്തിൽ തുരിശ് പ്ലാസ്റ്റിക് അല്ലെങ്കിൽ മൺപാത്രത്തിൽ ലയിപ്പിക്കുക.
   - മറ്റൊരു പാത്രത്തിൽ 50 ലിറ്റർ വെള്ളത്തിൽ നീറ്റുകക്ക ലയിപ്പിച്ച് കുമ്മായ ലായനി തയ്യാറാക്കുക.
   - തുരിശ് ലായനി പതുക്കെ കുമ്മായ ലായനിയിലേക്ക് ഒഴിച്ച് ഇളക്കുക.
3. **പ്രയോഗ സമയം:**
   - കാലവർഷം തുടങ്ങുന്നതിന് തൊട്ടുമുമ്പ് ആദ്യത്തെ സ്പ്രേയും, 40-45 ദിവസങ്ങൾക്ക് ശേഷം രണ്ടാമത്തെ സ്പ്രേയും നൽകുക."""
        }
    },
    "koleroga": {
        "keywords": ["koleroga", "mahali", "fruit rot", "rot", "dropping", "phytophthora", "ಕೊಳೆ", "ಕೊಳೆರೋಗ", "ಮಹಾಲಿ", "ಉದುರುವುದು", "सड़न", "कोलेरोगा", "കൊളെറോഗ", "കായ്ചീയൽ"],
        "replies": {
            "en": """### Mahali / Koleroga (Fruit Rot) Management Guide
- **Causal Organism:** *Phytophthora meadii* (water mold that thrives under continuous rain and >95% humidity).
- **Key Symptoms:** Water-soaked dark green lesions near calyx/stalk, rotting of kernel, heavy shedding of buttons and immature nuts, white fungal growth.
- **Immediate Interventions:**
  1. Spray 1% Bordeaux mixture thoroughly wetting bunches and crown canopy before monsoon rains.
  2. In high-rainfall areas, tie 100-gauge non-chlorinated polythene covers over bunches (cost-effective, chemical-free, 100% rainproof barrier).
  3. Collect and burn/destroy all fallen infected nuts and dead fronds to eliminate overwintering oospores.
  4. Ensure inter-drainage channels in the plantation to reduce ambient humidity.""",
            "kn": """### ಮಹಾಲಿ / ಕೊಳೆರೋಗ (ಕಾಯಿ ಕೊಳೆ) ಸಮಗ್ರ ನಿರ್ವಹಣೆ
- **ರೋಗದ ಮೂಲ:** *ಫೈಟೋಪ್ತೊರಾ ಮಿಯಾಡೈ* (Phytophthora meadii) ಎಂಬ ಶಿಲೀಂಧ್ರ.
- **ರೋಗದ ಲಕ್ಷಣಗಳು:** ಕಾಯಿಯ ತೊಟ್ಟಿನ ಬಳಿ ಎಣ್ಣೆ ಮೆತ್ತಿದಂತಹ ಕಪ್ಪು ಕಲೆಗಳು, ಹಸಿ ಅಡಿಕೆ ಗೊನೆಯಿಂದ ಉದುರುವುದು, ಕಳಚಿಬಿದ್ದ ಕಾಯಿಗಳ ಮೇಲೆ ಬಿಳಿ ಬಣ್ಣದ ಶಿಲೀಂಧ್ರ ಹರಡುವುದು.
- **ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳು:**
  ೧. ಮುಂಗಾರು ಮಳೆಗೆ ಮುನ್ನ ಗೊನೆ ಮತ್ತು ಕಿರೀಟಕ್ಕೆ ೧% ಬೋರ್ಡೋ ದ್ರಾವಣವನ್ನು ಸಮರ್ಪಕವಾಗಿ ಸಿಂಪಡಿಸಿ.
  ೨. ಮಳೆಗಾಲಕ್ಕೆ ಮುಂಚಿತವಾಗಿ ಗೊನೆಗಳಿಗೆ ೧೦೦ ಗೇಜ್‌ನ ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟುವುದು (ರಾಸಾಯನಿಕ ರಹಿತ ಮತ್ತು ಸಂಪೂರ್ಣ ರಕ್ಷಣೆ).
  ೩. ನೆಲಕ್ಕೆ ಉದುರಿದ ಕೊಳೆತ ಅಡಿಕೆಗಳನ್ನು ಆರಿಸಿ ತೋಟದಿಂದ ಹೊರಗೆ ಗುಂಡಿ ತೋಡಿ ಮುಚ್ಚಿ ಅಥವಾ ಸುಟ್ಟುಹಾಕಿ.
  ೪. ತೋಟದಲ್ಲಿ ಮಳೆ ನೀರು ನಿಲ್ಲದಂತೆ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ.""",
            "hi": """### महाली / कोलेरोगा (फल सड़न) प्रबंधन गाइड
- **कारण:** *फाइटोफ्थोरा मियाडी* कवक जो लगातार वर्षा और नमी में तेजी से फैलता है।
- **लक्षण:** डंठल के पास गहरे धब्बे, कच्चे फलों का गिरना, गिरे हुए फलों पर सफेद फफूंद।
- **रोकथाम:**
  1. मानसून पूर्व 1% बोर्डो मिश्रण का पहला छिड़काव और 40 दिन बाद दूसरा छिड़काव।
  2. गुच्छों पर 100-गेज पॉलिथीन कवर बांधना (वर्षा से सुरक्षित)।
  3. गिरे हुए संक्रमित फलों को एकत्र कर नष्ट करना।""",
            "ml": """### മഹാലി / കൊളെറോഗ (കായ്ചീയൽ) നിയന്ത്രണം
- **കാരണം:** *ഫൈറ്റോഫ്തോറ മിയാഡി* (Phytophthora meadii) കുമിൾ.
- **ലക്ഷണങ്ങൾ:** കായയുടെ ഞെട്ടിന് സമീപം കറുത്ത പാടുകൾ, അടക്ക കൊഴിയൽ, വീണ അടക്കയിൽ വെളുത്ത കുമിൾ വളർച്ച.
- **പരിഹാരം:**
  1. കാലവർഷത്തിന് മുമ്പ് 1% ബോർഡോ മിശ്രിതം സ്പ്രേ ചെയ്യുക.
  2. അടയ്ക്ക കുലകൾ പോളിത്തീൻ ഷീറ്റ് കൊണ്ട് പൊതിഞ്ഞു കെട്ടുക.
  3. വീണ രോഗബാധിത അടക്കകൾ ശേഖരിച്ച് നശിപ്പിക്കുക."""
        }
    },
    "yld": {
        "keywords": ["yellow", "yld", "chlorosis", "phytoplasma", "proutista", "ಹಳದಿ", "ವೈಎಲ್ಡಿ", "ಗರಿ", "पीला पत्ता", "മഞ്ഞളിപ്പ്"],
        "replies": {
            "en": """### Yellow Leaf Disease (YLD) Agronomic Management Guide
- **Causal Organism:** Phytoplasma (wall-less bacterium) transmitted by plant hoppers (*Proutista moesta*) and lacewing bugs.
- **Key Symptoms:** Conspicuous yellowing (chlorosis) beginning at leaflet tips on lower/middle whorls, black necrosis at leaf margin, root tip rot, yield decline.
- **Management Protocol (ICAR-CPCRI):**
  1. **Nutrient Rehabilitation:** Apply 100g N, 40g P2O5, 140g K2O per palm annually in two split doses. Add 1 kg neem cake and 12 kg organic compost per tree.
  2. **Magnesium Sulphate & Lime:** Apply 500g Agricultural Lime / Dolomite per palm once every two years to correct soil acidity (pH 6.0-6.5), and 150g Magnesium Sulphate annually.
  3. **Drainage:** Trench drainage channels (30cm wide x 60cm deep) between palm rows to prevent waterlogging and root asphyxiation.
  4. **Intercropping:** Introduce beneficial companion crops like Cocoa, Black Pepper, Banana, or Green manure (Velvet bean) to stabilize root-zone microclimate.""",
            "kn": """### ಹಳದಿ ಎಲೆ ರೋಗ (YLD) ಸಮಗ್ರ ನಿರ್ವಹಣಾ ಮಾರ್ಗಸೂಚಿ
- **ರೋಗದ ಮೂಲ:** ಫೈಟೋಪ್ಲಾಸ್ಮಾ (Phytoplasma) ಸೂಕ್ಷ್ಮಾಣುಜೀವಿ, ಜಿಗಿಹುಳುಗಳ (*Proutista moesta*) ಮೂಲಕ ಹರಡುತ್ತದೆ.
- **ರೋಗ ಲಕ್ಷಣಗಳು:** ಕೆಳಗಿನ ಗರಿಗಳ ತುದಿಯಲ್ಲಿ ಹಳದಿ ಬಣ್ಣ ಕಾಣಿಸಿಕೊಳ್ಳುವುದು, ಎಲೆ ಅಂಚು ಕಪ್ಪಾಗುವುದು, ಬೇರುಗಳು ಕೊಳೆಯುವುದು ಮತ್ತು ಇಳುವರಿ ಕುಸಿಯುವುದು.
- **ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು (ICAR-CPCRI ಶಿಫಾರಸು):**
  ೧. **ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ:** ವಾರ್ಷಿಕವಾಗಿ ಮರಕ್ಕೆ ೧೦೦ ಗ್ರಾಂ ಸಾರಜನಕ, ೪೦ ಗ್ರಾಂ ರಂಜಕ, ೧೪೦ ಗ್ರಾಂ ಪೊಟ್ಯಾಷ್ + ೧ ಕೆ.ಜಿ ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ೧೨ ಕೆ.ಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ನೀಡಿ.
  ೨. **ಸುಣ್ಣ ಮತ್ತು ಮೆಗ್ನೀಸಿಯಮ್:** ಮಣ್ಣಿನ ಆಮ್ಲೀಯತೆ ಸರಿಪಡಿಸಲು ೨ ವರ್ಷಕ್ಕೊಮ್ಮೆ ೫೦೦ ಗ್ರಾಂ ಕೃಷಿ ಸುಣ್ಣ ಮತ್ತು ವಾರ್ಷಿಕ ೧೫೦ ಗ್ರಾಂ ಮೆಗ್ನೀಸಿಯಮ್ ಸಲ್ಫೇಟ್ ಹಾಕಿ.
  ೩. **ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಣೆ:** ತೋಟದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಸಾಲುಗಳ ನಡುವೆ ಆಳವಾದ ಚರಂಡಿಗಳನ್ನು ನಿರ್ಮಿಸಿ.
  ೪. **ಮಿಶ್ರ ಬೆಳೆ ಪದ್ಧತಿ:** ಕೋಕೋ, ಕಾಳುಮೆಣಸು, ಬಾಳೆ ಮುಂತಾದ ಮಿಶ್ರ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಸಿ ತೋಟದ ತೇವಾಂಶ ಮತ್ತು ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಕಾಪಾಡಿ.""",
            "hi": """### पीला पत्ता रोग (YLD) प्रबंधन
- **कारण:** फाइटोप्लाज्मा जो कीड़ों द्वारा फैलता है।
- **लक्षण:** नीचे की पत्तियों के सिरों से पीलापन शुरू होकर फैलना, जड़ों का सड़ना।
- **प्रबंधन:**
  1. प्रति पेड़ 100 ग्राम N, 40 ग्राम P2O5, 140 ग्राम K2O + 12 किग्रा कम्पोस्ट।
  2. मिट्टी की अम्लता दूर करने के लिए 500 ग्राम कृषि चूना व 150 ग्राम मैग्नीशियम सल्फेट।
  3. जल निकासी की उचित व्यवस्था और कोको/काली मिर्च की अंतर-फसल।""",
            "ml": """### മഞ്ഞളിപ്പ് രോഗം (YLD) നിയന്ത്രണം
- **കാരണം:** ഫൈറ്റോപ്ലാസ്മ (Phytoplasma).
- **ലക്ഷണങ്ങൾ:** താഴത്തെ ഓലകളുടെ അഗ്രഭാഗത്ത് നിന്ന് മഞ്ഞനിറം പടരുക, വേര് ചീയൽ.
- **പരിപാലനം:**
  1. പ്രതിവർഷം 100g N, 40g P, 140g K + 12kg കമ്പോസ്റ്റ് + 1kg വേപ്പിൻപിണ്ണാക്ക്.
  2. 500g കുമ്മായവും 150g മഗ്നീഷ്യം സൾഫേറ്റും ചേർക്കുക.
  3. തോട്ടത്തിൽ നീർവാർച്ച സൗകര്യം ഉറപ്പാക്കുക, കൊക്കോ, കുരുമുളക് ഇടവിളയായി നടുക."""
        }
    },
    "fertilizer": {
        "keywords": ["fertilizer", "nutrient", "npk", "urea", "manure", "dose", "compost", "ಗೊಬ್ಬರ", "ಪೋಷಕಾಂಶ", "ಯೂರಿಯಾ", "ಖತ", "उर्वरक", "खाद", "വളം", "യൂറിയ"],
        "replies": {
            "en": """### Annual Fertilizer Schedule for Bearing Arecanut Palms (ICAR-CPCRI)
- **Standard Dose Per Mature Palm/Year:**
  - Nitrogen (N): 100 grams (~220g Urea)
  - Phosphorus (P2O5): 40 grams (~200g Rock Phosphate)
  - Potassium (K2O): 140 grams (~230g Muriate of Potash / MOP)
  - Organic Manure: 12 to 15 kg Farmyard Manure or Green Leaf Compost
- **Split Application Schedule:**
  - **1st Dose (Sept-Oct, post-monsoon):** 1/3 N (75g Urea) + Full P (200g Rock Phosphate) + 1/3 K (80g MOP) + Full Organic Manure.
  - **2nd Dose (May-June, pre-monsoon):** 2/3 N (145g Urea) + 2/3 K (150g MOP).
- **Application Method:** Spread in a circular basin of 0.75m to 1.0m radius around the palm, incorporate lightly into topsoil and irrigate.""",
            "kn": """### ಫಲ ನೀಡುವ ಅಡಿಕೆ ಮರಗಳಿಗೆ ವಾರ್ಷಿಕ ಗೊಬ್ಬರದ ಪ್ರಮಾಣ (ICAR-CPCRI)
- **ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕ ಪ್ರಮಾಣ:**
  - ಸಾರಜನಕ: ೧೦೦ ಗ್ರಾಂ (~೨೨೦ ಗ್ರಾಂ ಯೂರಿಯಾ)
  - ರಂಜಕ: ೪೦ ಗ್ರಾಂ (~೨೦೦ ಗ್ರಾಂ ರಾಕ್ ಫಾಸ್ಫೇಟ್)
  - ಪೊಟ್ಯಾಷ್: ೧೪೦ ಗ್ರಾಂ (~೨೩೦ ಗ್ರಾಂ ಮ್ಯೂರಿಯೇಟ್ ಆಫ್ ಪೊಟ್ಯಾಷ್ / MOP)
  - ಸಾವಯವ ಗೊಬ್ಬರ: ೧೨ ರಿಂದ ೧೫ ಕೆ.ಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಹಸಿರೆಲೆ ಗೊಬ್ಬರ
- **ನೀಡುವ ಹಂತಗಳು:**
  - **ಮೊದಲ ಕಂತು (ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್):** ೧/೩ ಸಾರಜನಕ + ಪೂರ್ಣ ರಂಜಕ + ೧/೩ ಪೊಟ್ಯಾಷ್ + ಪೂರ್ಣ ಸಾವಯವ ಗೊಬ್ಬರ.
  - **ಎರಡನೇ ಕಂತು (ಮೇ - ಜೂನ್):** ೨/೩ ಸಾರಜನಕ + ೨/೩ ಪೊಟ್ಯಾಷ್.
- **ಹಾಕುವ ವಿಧಾನ:** ಮರದ ಬುಡದಿಂದ ೧ ಮೀಟರ್ ದೂರದಲ್ಲಿ ವೃತ್ತಾಕಾರವಾಗಿ ಹರಡಿ ಮಣ್ಣಿನಲ್ಲಿ ಬೆರೆಸಿ ತೇವಾಂಶವಿರುವಂತೆ ನೀರು ಹಾಯಿಸಿ.""",
            "hi": """### सुपारी के लिए वार्षिक उर्वरक अनुशंसा (प्रति पेड़)
- **मात्रा:** 100g नाइट्रोजन (220g यूरिया), 40g फास्फोरस (200g रॉक फास्फेट), 140g पोटाश (230g MOP) तथा 12-15 किग्रा गोबर की खाद।
- **समय:** पहली खुराक सितंबर-अक्टूबर में और दूसरी खुराक मई-जून में पेड़ के तने से 1 मीटर की दूरी पर मिट्टी में मिलाएँ।""",
            "ml": """### കായ്ഫലമുള്ള കവുങ്ങിനുള്ള വാർഷിക വളപ്രയോഗം
- **ഒരു കവുങ്ങിന്:** 100g നൈട്രജൻ (220g യൂറിയ), 40g ഫോസ്ഫറസ് (200g റോക്ക് ഫോസ്ഫേറ്റ്), 140g പൊട്ടാഷ് (230g MOP), 12-15kg ജൈവവളം.
- **സമയം:** ഒന്നാം ഗഡു സെപ്റ്റംബർ-ഒക്ടോബറിലും രണ്ടാം ഗഡു മെയ്-ജൂണിലും തടത്തിൽ ചേർക്കുക."""
        }
    },
    "irrigation": {
        "keywords": ["water", "irrigation", "drip", "summer", "litres", "ನೀರು", "ನೀರಾವರಿ", "ಹನಿ", "सिंचाई", "पानी", "നന", "ജലസേചനം"],
        "replies": {
            "en": """### Arecanut Irrigation & Water Management
- **Water Requirement:** A bearing arecanut palm needs approximately **150 to 200 Litres of water every 4 to 5 days** during the dry summer months (or 16 to 20 Litres per day under drip irrigation).
- **Critical Periods:** November to May are critical irrigation months. Water stress during dry months causes button shedding, nut cracking, and stunted frond growth.
- **Mulching:** Cover the root basin (radius of 1m) with arecanut leaves, husk, or coir pith up to 5-10 cm thickness (leaving 15cm around trunk clear) to conserve moisture and reduce evaporation by 40%.
- **Monsoon Drainage:** Ensure drainage trenches are cleared before June; water stagnation causes root decay and collar rot.""",
            "kn": """### ಅಡಿಕೆ ತೋಟದ ನೀರಾವರಿ ನಿರ್ವಹಣೆ
- **ನೀರಿನ ಅವಶ್ಯಕತೆ:** ಬೇಸಿಗೆಯಲ್ಲಿ ಪ್ರತಿ ಮರಕ್ಕೆ ೪-೫ ದಿನಗಳಿಗೊಮ್ಮೆ ಸುಮಾರು ೧೫೦ ರಿಂದ ೨೦೦ ಲೀಟರ್ ನೀರು ಬೇಕಾಗುತ್ತದೆ (ಅಥವಾ ಹನಿ ನೀರಾವರಿಯಲ್ಲಿ ದಿನಕ್ಕೆ ೧೬-೨೦ ಲೀಟರ್).
- **ಮುಖ್ಯ ಅವಧಿ:** ನವೆಂಬರ್‌ನಿಂದ ಮೇ ತಿಂಗಳವರೆಗೆ ಸತತ ತೇವಾಂಶವಿರಬೇಕು. ತೇವಾಂಶ ಕೊರತೆಯಾದರೆ ಕಾಯಿ ಕಚ್ಚುವುದು ಕಡಿಮೆಯಾಗಿ ಪಿಂಡಿ ಉದುರುತ್ತದೆ.
- **ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್):** ಮರದ ಬುಡದ ಸುತ್ತಲೂ ಅಡಿಕೆ ಗರಿಗಳು ಅಥವಾ ಸಿಪ್ಪೆಯಿಂದ ಹೊದಿಕೆ ಮಾಡುವುದರಿಂದ ತೇವಾಂಶ ಆವಿಯಾಗುವುದನ್ನು ಶೇ. ೪೦ ರಷ್ಟು ತಡೆಯಬಹುದು.
- **ಬಸಿಗಾಲುವೆ:** ಮಳೆಗಾಲದಲ್ಲಿ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಕಾಲುವೆಗಳ ಮೂಲಕ ನೀರನ್ನು ಹೊರಹಾಕಿ.""",
            "hi": """### सुपारी में सिंचाई प्रबंधन
- गर्मी में प्रति पेड़ 150-200 लीटर पानी 4-5 दिनों के अंतराल पर दें (ड्रिप से 16-20 लीटर प्रतिदिन)।
- तने के चारों ओर पत्तियों या भूसी की मल्चिंग करें जिससे नमी संरक्षित रहे।""",
            "ml": """### കവുങ്ങിന്റെ ജലസേചനം
- വേനൽക്കാലത്ത് 4-5 ദിവസത്തിലൊരിക്കൽ 150-200 ലിറ്റർ വെള്ളം നൽകുക (തുള്ളിനന വഴി ദിവസം 16-20 ലിറ്റർ).
- തടത്തിൽ ചപ്പുചവറുകൾ കൊണ്ട് പുതയിടുന്നത് ഈർപ്പം നിലനിർത്താൻ സഹായിക്കും."""
        }
    }
}


def ask_agronomy_assistant(question, target_lang="en"):
    """
    Intelligent Agronomy Agent.
    Checks preloaded agronomic database first for instant expert replies,
    and calls Gemini AI for bespoke complex queries if API key is present.
    """
    q_lower = question.lower().strip()
    target_lang = target_lang if target_lang in ["en", "kn", "hi", "ml"] else "en"

    # 1. Semantic keyword matching against preloaded knowledge base
    matched_entry = None
    max_score = 0
    for topic_id, topic_data in PRELOADED_AGRONOMY_KB.items():
        score = sum(1 for kw in topic_data["keywords"] if kw in q_lower)
        if score > max_score:
            max_score = score
            matched_entry = topic_data

    # If high-confidence match found in preloaded KB, return immediately
    if matched_entry and max_score >= 1:
        reply_text = matched_entry["replies"].get(target_lang, matched_entry["replies"]["en"])
        return {
            "reply": reply_text,
            "source": "preloaded",
            "suggested_questions": [
                "How to prepare 1% Bordeaux mixture?",
                "Koleroga / Mahali prevention tips",
                "Annual fertilizer schedule for arecanut",
                "Yellow Leaf Disease management"
            ]
        }

    # 2. If no direct preloaded match and Gemini API key is available, query Gemini
    api_key = get_gemini_api_key()
    if api_key:
        system_prompt = (
            "You are ArecaLens Agronomy AI, an authoritative agricultural advisor specialized in arecanut (Areca catechu) palms, "
            "cultivation, pathology (Koleroga/Mahali, Yellow Leaf Disease, Anabe Roga), and ICAR-CPCRI agronomic guidelines. "
            f"Respond clearly, concisely, and practically in language: {target_lang}. "
            "Use bullet points and bold section headers. Avoid filler or robotic pleasantries."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt + "\n\nFarmer Question: " + question}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 600
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                raw_text = resp_data['candidates'][0]['content']['parts'][0]['text']
                return {
                    "reply": raw_text.strip(),
                    "source": "gemini",
                    "suggested_questions": [
                        "How to prepare 1% Bordeaux mixture?",
                        "Yellow Leaf Disease management",
                        "Fertilizer dose per palm"
                    ]
                }
        except Exception as e:
            logger.warning("Gemini AI query failed: %s; falling back to agronomy guidelines.", e)

    # 3. Default fallback agronomic response
    fallbacks = {
        "en": """### ArecaLens Agronomy Advisory
For arecanut palm health and cultivation questions:
- **Koleroga (Fruit Rot):** Apply 1% Bordeaux mixture before South-West monsoon and consider 100-gauge polythene bunch covering.
- **Yellow Leaf Disease:** Ensure balanced NPK (100:40:140g), apply 500g lime to acidic soil, and construct deep drainage trenches.
- **Fertilizer Dose:** 220g Urea, 200g Rock Phosphate, 230g Potash per palm annually in two split doses.
- **Authority Support:** Consult the nearest ICAR-CPCRI Research Station (Kasaragod / Vittal) or local Krishi Vigyan Kendra (KVK).""",
        "kn": """### ಅಡಿಕೆ ಕೃಷಿ ಸಲಹಾ ಕೇಂದ್ರ
ಅಡಿಕೆ ಬೆಳೆಯ ಆರೋಗ್ಯ ಮತ್ತು ಪೋಷಣೆಗಾಗಿ ಪ್ರಮುಖ ಶಿಫಾರಸುಗಳು:
- **ಕೊಳೆರೋಗ ತಡೆಗಟ್ಟಲು:** ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ ೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ ಅಥವಾ ಗೊನೆಗಳಿಗೆ ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟಿ.
- **ಹಳದಿ ಎಲೆ ರೋಗಕ್ಕೆ:** ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ (೧೦೦:೪೦:೧೪೦ ಗ್ರಾಂ), ಆಮ್ಲೀಯ ಮಣ್ಣಿಗೆ ಸುಣ್ಣ ಹಾಗೂ ತೋಟದಲ್ಲಿ ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಣೆ ಮಾಡಿ.
- **ಗೊಬ್ಬರ ಪ್ರಮಾಣ:** ವಾರ್ಷಿಕವಾಗಿ ಮರಕ್ಕೆ ೨೨೦ ಗ್ರಾಂ ಯೂರಿಯಾ, ೨೦೦ ಗ್ರಾಂ ರಾಕ್ ಫಾಸ್ಫೇಟ್, ೨೩೦ ಗ್ರಾಂ ಪೊಟ್ಯಾಷ್ ಅನ್ನು ಎರಡು ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.
- **ಹೆಚ್ಚಿನ ನೆರವಿಗೆ:** ಸಮೀಪದ ICAR-CPCRI ಕಾಸರಗೋಡು / ವಿಟ್ಲ ಸಂಶೋಧನಾ ಕೇಂದ್ರ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ.""",
        "hi": """### सुपारी कृषि सलाहकार
- **कोलेरोगा:** मानसून पूर्व 1% बोर्डो मिश्रण का छिड़काव करें अथवा गुच्छों पर कवर बांधें।
- **पीला पत्ता रोग:** संतुलित NPK (100:40:140g), कृषि चूना और जल निकासी की व्यवस्था करें।
- **उर्वरक:** प्रति पेड़ 220g यूरिया, 200g रॉक फॉस्फेट, 230g पोटाश दो भागों में दें।""",
        "ml": """### അടയ്ക്ക കൃഷി സഹായി
- **കായ്ചീയൽ:** കാലവർഷത്തിന് മുമ്പ് 1% ബോർഡോ മിശ്രിതം തളിക്കുക.
- **മഞ്ഞളിപ്പ്:** സമീകൃത വളപ്രയോഗം (100:40:140g), നീർവാർച്ച ഉറപ്പാക്കുക.
- **കൂടുതൽ വിവരങ്ങൾക്ക്:** ICAR-CPCRI കാസർഗോഡ് കേന്ദ്രവുമായി ബന്ധപ്പെടുക."""
    }
    return {
        "reply": fallbacks.get(target_lang, fallbacks["en"]),
        "source": "preloaded",
        "suggested_questions": [
            "How to prepare 1% Bordeaux mixture?",
            "Koleroga / Mahali prevention tips",
            "Annual fertilizer schedule for arecanut"
        ]
    }
