/**

 * ArecaLens — Client-side Interactive Engine

 * Faithful Replication of Reference Video UI & Interactions

 */



document.addEventListener('DOMContentLoaded', function () {

  // Web Audio Tactile Synthesizer (Safe Top Declaration)

  let audioCtx = null;

  let isSoundEnabled = localStorage.getItem('arecalens_sound') !== 'muted';



  function playSoundCue(type) {

    if (!isSoundEnabled) return;

    try {

      if (!audioCtx) {

        const AudioCtxClass = window.AudioContext || window.webkitAudioContext;

        if (AudioCtxClass) audioCtx = new AudioCtxClass();

      }

      if (!audioCtx) return;

      if (audioCtx.state === 'suspended') {

        audioCtx.resume();

      }



      const now = audioCtx.currentTime;

      if (type === 'click') {

        const osc = audioCtx.createOscillator();

        const gain = audioCtx.createGain();

        osc.type = 'sine';

        osc.frequency.setValueAtTime(850, now);

        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.04);

        gain.gain.setValueAtTime(0.08, now);

        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

        osc.connect(gain);

        gain.connect(audioCtx.destination);

        osc.start(now);

        osc.stop(now + 0.04);

      } else if (type === 'shutter') {

        const osc = audioCtx.createOscillator();

        const gain = audioCtx.createGain();

        osc.type = 'triangle';

        osc.frequency.setValueAtTime(400, now);

        osc.frequency.exponentialRampToValueAtTime(80, now + 0.09);

        gain.gain.setValueAtTime(0.2, now);

        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);

        osc.connect(gain);

        gain.connect(audioCtx.destination);

        osc.start(now);

        osc.stop(now + 0.09);

      } else if (type === 'success') {

        [

          { freq: 523.25, time: now, dur: 0.12 },

          { freq: 659.25, time: now + 0.1, dur: 0.22 }

        ].forEach(t => {

          const osc = audioCtx.createOscillator();

          const gain = audioCtx.createGain();

          osc.type = 'sine';

          osc.frequency.setValueAtTime(t.freq, t.time);

          gain.gain.setValueAtTime(0.12, t.time);

          gain.gain.exponentialRampToValueAtTime(0.001, t.time + t.dur);

          osc.connect(gain);

          gain.connect(audioCtx.destination);

          osc.start(t.time);

          osc.stop(t.time + t.dur);

        });

      }

    } catch (e) {

      // Graceful fallback

    }

  }



  // =========================================================================

    function updateSoundUI() {

    const soundToggleBtn = document.getElementById('sound-toggle-btn');

    const soundIcon = document.getElementById('sound-icon');

    const soundLabel = document.getElementById('sound-label');

    const lang = (typeof currentLang !== 'undefined' && currentLang) ? currentLang : 'en';

    const strings = (typeof I18N_STRINGS !== 'undefined' && I18N_STRINGS[lang]) 

      ? I18N_STRINGS[lang] 

      : (typeof I18N_STRINGS !== 'undefined' && I18N_STRINGS['en'] ? I18N_STRINGS['en'] : {});



    if (soundIcon) soundIcon.textContent = isSoundEnabled ? '🔊' : '🔇';

    if (soundLabel) soundLabel.textContent = isSoundEnabled ? (strings.sound_label || 'Sound') : (strings.sound_muted || 'Muted');

    if (soundToggleBtn) {

      soundToggleBtn.setAttribute('title', isSoundEnabled ? 'Mute sound feedback' : 'Enable sound feedback');

      if (!isSoundEnabled) {

        soundToggleBtn.classList.add('muted');

      } else {

        soundToggleBtn.classList.remove('muted');

      }

    }

  }



  // 1. Comprehensive Regional Multi-Language Dictionary & Localization Engine

  // =========================================================================

  const I18N_STRINGS = {

  "en": {

    "lang_name": "English",

    "brand_tagline": "YOUR PLANT HEALTH COMPANION",

    "nav_analyze": "Analyze",

    "nav_guide": "Disease guide",

    "nav_history": "Scan history",
    "nav_architecture": "Architecture",

    "sound_label": "Sound",

    "sound_muted": "Muted",

    "model_ready": "Model ready",

    "modal_badge": "ARECALENS",

    "step_welcome": "Welcome",

    "step_input": "Specimen Input",

    "step_analyzing": "Analysis HUD",

    "step_results": "Results & XAI",

    "step_dossier": "Disease Dossier",

    "vol_chap_1": "VOLUME I • CHAPTER 1",

    "vol_chap_2": "VOLUME I • CHAPTER 2",

    "vol_chap_3": "VOLUME I • CHAPTER 3",

    "vol_chap_4": "VOLUME I • CHAPTER 4",

    "vol_chap_5": "VOLUME I • CHAPTER 5",

    "page_1_of_5": "Page 1 of 5",

    "page_2_of_5": "Page 2 of 5",

    "page_3_of_5": "Page 3 of 5",

    "page_4_of_5": "Page 4 of 5",

    "page_5_of_5": "Page 5 of 5",

    "hero_tag": "AI-Powered Phytosanitary Diagnostics • ResNet-50",

    "hero_title": "Care for your arecanut. Understand what you see.",
    "hero_split_eyebrow": "FOR THE PEOPLE WHO GROW",
    "hero_split_title": "Care for your<br>arecanut.<br>Understand what<br>you see.",
    "hero_split_desc": "Take a photo of a leaf or nut. Get a screening suggestion, see what the AI noticed, and learn what to check next.",
    "btn_get_started": "Get started",
    "hero_flow_label": "Photo → Screening → Explanation",
    "lang_pane_tag": "STEP 1 OF 2 • SELECT INTERFACE LANGUAGE",
    "lang_pane_title": "Choose your language",
    "lang_pane_sub": "Select your preferred language. AI diagnostics, pathology reports, and agronomic care guidelines will be personalized for you.",
    "btn_continue_inspect": "Continue to Specimen Input",
    "btn_back": "Back",

    "hero_desc": "An interactive, page-by-page diagnostic compendium engineered for arecanut palm cultivation. Combines 50-layer deep residual vision with Grad-CAM Explainable AI (XAI) and verified ICAR-CPCRI agronomic care protocols.",

    "feat_classes_title": "4 Pathology Classes",

    "feat_classes_desc": "Healthy Leaf, Healthy Nut, Mahali Fruit Rot, Yellow Leaf Disease.",

    "feat_layers_title": "50 Residual Layers",

    "feat_layers_desc": "Deep bottleneck feature extraction trained on high-resolution field specimens.",

    "feat_xai_title": "Explainable AI (XAI)",

    "feat_xai_desc": "Real-time Grad-CAM heatmaps illuminate the exact leaf and nut features analyzed.",

    "feat_edge_title": "100% Edge Processing",

    "feat_edge_desc": "Zero third-party APIs. Private, secure, and executed directly on this server.",

    "btn_start_inspect": "Start Inspection",

    "btn_browse_dossier": "Browse Disease Dossier",

    "upload_card_title": "Add a plant photo",

    "upload_sub": "Upload a photo or capture with live camera",

    "upload_card_tag": "Leaf or nut",

    "dropzone_title": "A good photo makes a difference.",

    "dropzone_sub": "Drop a photo here or choose an option below.",

    "btn_choose_image": "Choose image",

    "btn_use_camera": "Use camera",

    "dropzone_formats": "JPG, JPEG or PNG • max 10MB",

    "change_photo": "Change photo",

    "samples_heading": "⚡ Instant Test Samples (Click to load specimen):",

    "sample_healthy_leaf": "🍃 Healthy Leaf",

    "sample_healthy_nut": "🌰 Healthy Nut",

    "sample_mahali": "🍄 Mahali Rot",

    "sample_yld": "🍂 Yellow Leaf",

    "btn_analyze": "Analyze plant health ↗",

    "btn_analyzing": "Analyzing your photo...",

    "tips_card_title": "A good photo makes a difference.",

    "tips_card_sub": "A clear view helps the model. Avoid hands covering the plant and very busy backgrounds.",

    "tip_1_title": "Use natural daylight",

    "tip_1_desc": "Clear, natural lighting helps avoid misleading shadows.",

    "tip_2_title": "Fill the frame with one leaf or nut",

    "tip_2_desc": "Get close enough so the affected area is prominent.",

    "tip_3_title": "Hold the camera steady",

    "tip_3_desc": "Sharp focus prevents blur from distorting diagnostic signals.",

    "tips_disclaimer": "Photo screening can be wrong. Expert confirmation matters.",

    "btn_turn_back_welcome": "◂ Turn Back to Welcome",

    "btn_run_screening": "Run Screening & XAI Analysis",

    "hud_headline": "Scanning Specimen & Computing Grad-CAM...",

    "hud_caption": "Executing 50-layer deep residual inference and backpropagating layer4 gradients to construct attention heatmaps.",

    "phase_1_text": "[1] Ingesting Specimen & Normalizing 224x224 RGB Tensor",

    "phase_2_text": "[2] Extracting 2048-dim Feature Vectors across 50 ResNet Residual Blocks",

    "phase_3_text": "[3] Grad-CAM Gradient Backpropagation on layer4 Bottleneck",

    "phase_4_text": "[4] Compiling ICAR-CPCRI Agronomic Advisory & Disease Dossier",

    "awaiting_screening": "Awaiting specimen screening. Input an image on Page 2 and click Analyze.",

    "showing_diagnosis": "Showing automated screening diagnosis for",

    "analyze_another_photo": "Analyze another photo ➔",

    "badge_suspected": "Disease pattern suspected",

    "badge_healthy": "Healthy plant",

    "badge_review": "This photo needs another look.",

    "advisory_caption": "A suggestion from this photo. Check the plant and consider expert advice.",

    "score_label": "Relative model score",

    "score_sub": "Across compare four model classes. It is not the chance that the diagnosis is correct.",

    "see_all_scores": "▴ Hide four model scores",

    "see_all_scores_open": "▾ See all four model scores",

    "primary_match": "PRIMARY MATCH",

    "understanding_title": "Understanding this result",

    "copy_advisory": "Copy Advisory",

    "advisory_copied": "✓ Copied!",

    "influenced_title": "What influenced the result?",

    "tab_model_input": "Model input",

    "tab_cam_overlay": "CAM overlay",

    "tab_compare": "Compare",

    "tab_curtain": "Curtain ◂▸",

    "curtain_model_input": "Model Input",

    "curtain_heatmap": "Grad-CAM Heatmap",

    "overlay_opacity": "Overlay opacity",

    "less_contrib": "Less contribution",

    "more_contrib": "More contribution",

    "cam_caption": "Warm colours show stronger contribution to the chosen class. They do not confirm a diseased area or its cause.",

    "layer_tag": "Layer: ResNet-50 • layer4",

    "latency_tag": "Latency:",

    "btn_scan_another": "◂ Scan Another Specimen",

    "btn_turn_dossier": "Turn to Disease Dossier",

    "btn_turn_back_results": "◂ Turn Back to Results & XAI (Page 4)",

    "dossier_headline": "Phytosanitary Compendium & Agronomic Dossier",

    "dossier_lead": "Comprehensive biological analysis of the four arecanut classes: causal organisms, pathological progression, ICAR-CPCRI management protocols, and comparative trade-offs.",

    "tab_dossier_mahali": "🍄 Mahali / Koleroga (Fruit Rot)",

    "tab_dossier_yld": "🍂 Yellow Leaf Disease (YLD)",

    "tab_dossier_healthy_nut": "🌰 Healthy Nut (Control)",

    "tab_dossier_healthy_leaf": "🍃 Healthy Leaf (Control)",

    "btn_turn_back_input": "◂ Turn Back to Specimen Input",

    "btn_start_new_inspect": "Start New Inspection",

    "lang_modal_title": "Choose your language",

    "lang_modal_sub": "Choose the language you are comfortable with. You can change it any time.",

    "btn_continue": "Continue ➔",

    "lang_disclaimer": "Regional translations are drafts. Verified agronomist advice overrides all screening.",

    "history_title": "Your recent observations",

    "history_sub": "The latest eight scans on this device. Clearing browser data removes them.",

    "clear_history": "Clear history",

    "no_history": "No past scans recorded on this device yet.",

    "empty_history_desc": "Upload or capture an arecanut leaf or nut specimen to automatically retain diagnostic records.",

    "history_tag_healthy": "HEALTHY CONTROL",

    "history_tag_diseased": "DISEASE PATTERN SUSPECTED",

    "history_score_label": "Relative score:",

    "camera_modal_title": "Live Specimen Camera Studio",

    "camera_guide_label": "Align Leaf or Nut Inside Reticle",

    "footer_slogan": "A locally-run tool to assist—never the final diagnosis.",

    "footer_methodology": "Methodology",

    "about_tag": "Phytosanitary AI Methodology",

    "about_title": "Technical Architecture & Pathology",

    "about_desc": "Comprehensive specification of the transfer-learned ResNet-50 architecture, Grad-CAM layer4 explainability engine, and 4-class agronomic pathology taxonomy.",

    "about_launch_btn": "Launch Screening",

    "about_guide_btn": "Explore Field Guide ↗",

    "about_card1_title": "Neural Network Architecture",

    "about_card1_sub": "Transfer learning with deep residual feature representations",

    "about_card1_p1": "ArecaLens utilizes a fine-tuned deep residual network (ResNet-50) pretrained on ImageNet and specialized for foliar and nut pathologies of the Areca catechu palm.",

    "about_backbone_label": "Backbone:",

    "about_backbone_desc": "50 convolutional layers with residual shortcut connections",

    "about_head_label": "Classification Head:",

    "about_head_desc": "Modified 4-output linear layer (2048 → 4 classes)",

    "about_tensor_label": "Input Tensor:",

    "about_tensor_desc": "224 × 224 × 3 (RGB normalized via ImageNet μ=[0.485, 0.456, 0.406], σ=[0.229, 0.224, 0.225])",

    "about_xai_label": "Explainability:",

    "about_xai_desc": "Grad-CAM targeted at the terminal residual block (layer4, 2048 channels)",

    "about_infer_label": "Inference Mode:",

    "about_infer_desc": "Deterministic forward evaluation under torch.no_grad() with sub-100ms latency",

    "about_card2_title": "Explainable AI (Grad-CAM)",

    "about_card2_sub": "Gradient-weighted Class Activation Mapping",

    "about_card2_p1": "To provide actionable transparency for growers, the model computes neuron importance weights by taking gradients of the class score with respect to feature activation maps of the final convolutional layer:",

    "about_card2_p2": "The positive rectification (ReLU) isolates visual features that contribute positively to the predicted pathology, rendered as a continuous thermal heatmap blended over the original image at 45% default opacity.",

    "about_tax_title": "4-Class Pathological Taxonomy",

    "about_tax_sub": "Agronomic characteristics, etiology, and intervention standards",

    "status_healthy": "Healthy",

    "status_diseased": "Diseased",

    "recom_action_label": "Recommended Action:",

    "desc_healthy_nut": "Unblemished fruit specimen exhibiting typical morphology, uniform coloration, and absence of necrotic lesions or fungal mycelia.",

    "mgmt_healthy_nut": "Maintain regular irrigation schedule, soil nutrient management (NPK), and prophylactic canopy inspection.",

    "desc_healthy_leaf": "Vibrant green arecanut frond displaying standard chloroplastic pigmentation with no signs of yellowing, necrosis, or foliar blights.",

    "mgmt_healthy_leaf": "Continue standard horticultural practices; ensure adequate drainage during monsoon periods to prevent root stress.",

    "desc_mahali": "Destructive fruit rot of arecanut caused by the oomycete pathogen Phytophthora meadii McRae, causing water-soaked lesions, nut rotting, and heavy fruit shedding.",

    "mgmt_mahali": "Spray 1% Bordeaux mixture before monsoon onset; repeat after 40-45 days. Cover tender bunches with 125-gauge polythene bags.",

    "desc_yellow_leaf_disease": "Debilitating systemic disorder associated with phytoplasma transmitted by plant hoppers, causing progressive foliar chlorosis and crown reduction.",

    "mgmt_yellow_leaf_disease": "Apply balanced NPK with additional magnesium and organic manure. Improve soil drainage and manage vector populations."

  },

  "kn": {

    "lang_name": "ಕನ್ನಡ",

    "brand_tagline": "ನಿಮ್ಮ ಸಸ್ಯ ಆರೋಗ್ಯ ಒಡನಾಡಿ",

    "nav_analyze": "ವಿಶ್ಲೇಷಣೆ",

    "nav_guide": "ರೋಗ ಮಾಹಿತಿ",

    "nav_history": "ಇತಿಹಾಸ",
    "nav_architecture": "ವಾಸ್ತುಶಿಲ್ಪ",

    "sound_label": "ಧ್ವನಿ",

    "sound_muted": "ಮ್ಯೂಟ್ ಆಗಿದೆ",

    "model_ready": "ಮಾದರಿ ಸಿದ್ಧವಾಗಿದೆ",

    "modal_badge": "ಅಡಿಕೆಲೆನ್ಸ್",

    "step_welcome": "ಸ್ವಾಗತ",

    "step_input": "ಮಾದರಿ ಇನ್‌ಪುಟ್",

    "step_analyzing": "ವಿಶ್ಲೇಷಣೆ ಹಡ್",

    "step_results": "ಫಲಿತಾಂಶ & XAI",

    "step_dossier": "ರೋಗ ಕೋಶ",

    "vol_chap_1": "ಸಂಪುಟ ೧ • ಅಧ್ಯಾಯ ೧",

    "vol_chap_2": "ಸಂಪುಟ ೧ • ಅಧ್ಯಾಯ ೨",

    "vol_chap_3": "ಸಂಪುಟ ೧ • ಅಧ್ಯಾಯ ೩",

    "vol_chap_4": "ಸಂಪುಟ ೧ • ಅಧ್ಯಾಯ ೪",

    "vol_chap_5": "ಸಂಪುಟ ೧ • ಅಧ್ಯಾಯ ೫",

    "page_1_of_5": "ಪುಟ ೧/೫",

    "page_2_of_5": "ಪುಟ ೨/೫",

    "page_3_of_5": "ಪುಟ ೩/೫",

    "page_4_of_5": "ಪುಟ ೪/೫",

    "page_5_of_5": "ಪುಟ ೫/೫",

    "hero_tag": "ಎಐ ಆಧಾರಿತ ಸಸ್ಯ ರೋಗ ತಪಾಸಣೆ • ResNet-50",

    "hero_title": "ನಿಮ್ಮ ಅಡಿಕೆ ತೋಟದ ಆರೈಕೆ. ಕಂಡದ್ದನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ.",
    "hero_split_eyebrow": "ಬೆಳೆಗಾರರಿಗಾಗಿ",
    "hero_split_title": "ನಿಮ್ಮ ಅಡಿಕೆ ತೋಟದ<br>ಆರೈಕೆ.<br>ಕಂಡದ್ದನ್ನು ಸ್ಪಷ್ಟವಾಗಿ<br>ತಿಳಿಯಿರಿ.",
    "hero_split_desc": "ಎಲೆ ಅಥವಾ ಅಡಿಕೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ. ತಪಾಸಣಾ ಸಲಹೆ ಪಡೆಯಿರಿ, ಎಐ ಗುರುತಿಸಿದ್ದನ್ನು ವೀಕ್ಷಿಸಿ ಮತ್ತು ಮುಂದೇನು ಮಾಡಬೇಕೆಂದು ತಿಳಿಯಿರಿ.",
    "btn_get_started": "ಪ್ರಾರಂಭಿಸಿ",
    "hero_flow_label": "ಫೋಟೋ → ತಪಾಸಣೆ → ವಿವರಣೆ",
    "lang_pane_tag": "ಹಂತ ೧ • ಇಂಟರ್‌ಫೇಸ್ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    "lang_pane_title": "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    "lang_pane_sub": "ನಿಮಗೆ ಸರಿಹೊಂದುವ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ. ಎಐ ರೋಗ ಪತ್ತೆ ಮತ್ತು ಕೃಷಿ ಆರೈಕೆ ಮಾರ್ಗಸೂಚಿಗಳು ಈ ಭಾಷೆಯಲ್ಲಿ ಲಭ್ಯವಾಗುತ್ತವೆ.",
    "btn_continue_inspect": "ಮಾದರಿ ಇನ್‌ಪುಟ್‌ಗೆ ಮುಂದುವರಿಯಿರಿ",
    "btn_back": "ಹಿಂದೆ",

    "hero_desc": "ಅಡಿಕೆ ಕೃಷಿಗಾಗಿ ರೂಪಿಸಲಾದ ಸಂವಾದಾತ್ಮಕ ಪುಟವಾರು ರೋಗ ತಪಾಸಣಾ ವಿಶ್ವಕೋಶ. ೫೦-ಪದರದ ಡೀಪ್ ರೆಸಿಡ್ಯುಯಲ್ ವಿಶನ್, Grad-CAM ವಿವರಣಾತ್ಮಕ ಎಐ (XAI) ಮತ್ತು ದೃಢೀಕೃತ ICAR-CPCRI ಕೃಷಿ ಆರೈಕೆ ಮಾರ್ಗಸೂಚಿಗಳನ್ನು ಒಳಗೊಂಡಿದೆ.",

    "feat_classes_title": "೪ ರೋಗ ವರ್ಗಗಳು",

    "feat_classes_desc": "ಆರೋಗ್ಯಕರ ಎಲೆ, ಆರೋಗ್ಯಕರ ಅಡಿಕೆ, ಮಹಾಲಿ ಕೊಳೆರೋಗ, ಹಳದಿ ಎಲೆ ರೋಗ.",

    "feat_layers_title": "೫೦ ರೆಸಿಡ್ಯುಯಲ್ ಲೇಯರ್‌ಗಳು",

    "feat_layers_desc": "ಉನ್ನತ ರೆಸಲ್ಯೂಶನ್ ತೋಟದ ಮಾದರಿಗಳ ಮೇಲೆ ತರಬೇತಿ ಪಡೆದ ಡೀಪ್ ಬಾಟಲ್‌ನೆಕ್ ವೈಶಿಷ್ಟ್ಯ ಹೊರತೆಗೆಯುವಿಕೆ.",

    "feat_xai_title": "ವಿವರಣಾತ್ಮಕ ಎಐ (XAI)",

    "feat_xai_desc": "ರಿಯಲ್-ಟೈಮ್ Grad-CAM ಹೀಟ್‌ಮ್ಯಾಪ್‌ಗಳು ಮಾದರಿ ವಿಶ್ಲೇಷಿಸಿದ ನಿಖರ ಎಲೆ ಮತ್ತು ಅಡಿಕೆಯ ಭಾಗಗಳನ್ನು ತೋರಿಸುತ್ತವೆ.",

    "feat_edge_title": "೧೦೦% ಸ್ಥಳೀಯ ಸಂಸ್ಕರಣೆ",

    "feat_edge_desc": "ಯಾವುದೇ ಮೂರನೇ ವ್ಯಕ್ತಿಯ API ಇಲ್ಲ. ಖಾಸಗಿ, ಸುರಕ್ಷಿತ ಮತ್ತು ನೇರವಾಗಿ ಈ ಸರ್ವರ್‌ನಲ್ಲೇ ನಡೆಯುತ್ತದೆ.",

    "btn_start_inspect": "ಪರೀಕ್ಷೆ ಪ್ರಾರಂಭಿಸಿ",

    "btn_browse_dossier": "ರೋಗ ಮಾಹಿತಿ ಕೋಶ ನೋಡಿ",

    "upload_card_title": "ಗಿಡದ ಫೋಟೋ ಸೇರಿಸಿ",

    "upload_sub": "ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಲೈವ್ ಕ್ಯಾಮೆರಾದಲ್ಲಿ ಸೆರೆಹಿಡಿಯಿರಿ",

    "upload_card_tag": "ಎಲೆ ಅಥವಾ ಅಡಿಕೆ",

    "dropzone_title": "ಸ್ಪಷ್ಟ ಫೋಟೋ ಉತ್ತಮ ಮಾಹಿತಿಗೆ ಸಹಕಾರಿ.",

    "dropzone_sub": "ಫೋಟೋ ಇಲ್ಲಿ ಎಳೆಯಿರಿ ಅಥವಾ ಕೆಳಗಿನ ಆಯ್ಕೆಯನ್ನು ಬಳಸಿ.",

    "btn_choose_image": "ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",

    "btn_use_camera": "ಕ್ಯಾಮೆರಾ ಬಳಸಿ",

    "dropzone_formats": "JPG, JPEG ಅಥವಾ PNG • ಗರಿಷ್ಠ 10MB",

    "change_photo": "ಫೋಟೋ ಬದಲಾಯಿಸಿ",

    "samples_heading": "⚡ ತ್ವರಿತ ಪರೀಕ್ಷಾ ಮಾದರಿಗಳು (ಮಾದರಿಯನ್ನು ಲೋಡ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ):",

    "sample_healthy_leaf": "🍃 ಆರೋಗ್ಯಕರ ಎಲೆ",

    "sample_healthy_nut": "🌰 ಆರೋಗ್ಯಕರ ಅಡಿಕೆ",

    "sample_mahali": "🍄 ಮಹಾಲಿ ಕೊಳೆ",

    "sample_yld": "🍂 ಹಳದಿ ಎಲೆ",

    "btn_analyze": "ಗಿಡದ ಆರೋಗ್ಯ ಪರೀಕ್ಷಿಸಿ ↗",

    "btn_analyzing": "ಫೋಟೋ ಪರೀಕ್ಷಿಸಲಾಗುತ್ತಿದೆ...",

    "tips_card_title": "ಸ್ಪಷ್ಟ ಫೋಟೋ ಉತ್ತಮ ಮಾಹಿತಿಗೆ ಸಹಕಾರಿ.",

    "tips_card_sub": "ಸ್ಪಷ್ಟ ನೋಟವು ಮಾದರಿಗೆ ನಿಖರ ತಪಾಸಣೆಗೆ ನೆರವಾಗುತ್ತದೆ. ಕೈಗಳಿಂದ ಎಲೆ ಮುಚ್ಚಬೇಡಿ ಮತ್ತು ಅತಿಯಾದ ಹಿನ್ನೆಲೆ ತಪ್ಪಿಸಿ.",

    "tip_1_title": "ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಫೋಟೋ ತೆಗೆಯಿರಿ",

    "tip_1_desc": "ಹಗಲಿನ ನೈಸರ್ಗಿಕ ಬೆಳಕು ನೆರಳುಗಳ ಗೊಂದಲ ತಪ್ಪಿಸುತ್ತದೆ.",

    "tip_2_title": "ಫ್ರೇಮ್‌ನಲ್ಲಿ ಒಂದು ಎಲೆ ಅಥವಾ ಕಾಯಿ ಇರಲಿ",

    "tip_2_desc": "ಬಾಧಿತ ಭಾಗವು ದೊಡ್ಡದಾಗಿ ಕಾಣುವಂತೆ ಹತ್ತಿರದಿಂದ ಫೋಟೋ ತೆಗೆಯಿರಿ.",

    "tip_3_title": "ಕ್ಯಾಮೆರಾ ಸ್ಥಿರವಾಗಿರಲಿ",

    "tip_3_desc": "ಅಸ್ಪಷ್ಟ ಫೋಟೋ ರೋಗ ಗುರುತಿಸುವಿಕೆಯ ಸಂಕೇತಗಳನ್ನು ತಪ್ಪಿಸಬಹುದು.",

    "tips_disclaimer": "ಫೋಟೋ ತಪಾಸಣೆ ಅಂತಿಮವಲ್ಲ. ಕೃಷಿ ಅಧಿಕಾರಿಯ ದೃಢೀಕರಣ ಮುಖ್ಯ.",

    "btn_turn_back_welcome": "◂ ಸ್ವಾಗತ ಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ",

    "btn_run_screening": "ತಪಾಸಣೆ ಮತ್ತು XAI ವಿಶ್ಲೇಷಣೆ ನಡೆಸಿ",

    "hud_headline": "ಮಾದರಿ ಸ್ಕ್ಯಾನ್ ಮಾಡಲಾಗುತ್ತಿದೆ ಮತ್ತು Grad-CAM ಲೆಕ್ಕಾಚಾರ...",

    "hud_caption": "೫೦-ಪದರದ ಡೀಪ್ ರೆಸಿಡ್ಯುಯಲ್ ನೆಟ್‌ವರ್ಕ್ ಮತ್ತು Grad-CAM ಹೀಟ್‌ಮ್ಯಾಪ್ ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ.",

    "phase_1_text": "[೧] ಮಾದರಿ ಸ್ವೀಕಾರ ಮತ್ತು 224x224 RGB ಟೆನ್ಸರ್ ನಾರ್ಮಲೈಸೇಶನ್",

    "phase_2_text": "[೨] ೫೦ ರೆಸ್‌ನೆಟ್ ಬ್ಲಾಕ್‌ಗಳಲ್ಲಿ ೨೦೪೮-ಆಯಾಮದ ವೈಶಿಷ್ಟ್ಯಗಳ ವಿಶ್ಲೇಷಣೆ",

    "phase_3_text": "[೩] layer4 ಬಾಟಲ್‌ನೆಕ್‌ನಲ್ಲಿ Grad-CAM ಗ್ರೇಡಿಯಂಟ್ ಬ್ಯಾಕ್‌ಪ್ರೊಪಾಗೇಶನ್",

    "phase_4_text": "[೪] ICAR-CPCRI ಕೃಷಿ ಸಲಹೆ ಮತ್ತು ರೋಗ ವರದಿ ಸಿದ್ಧಪಡಿಸುವಿಕೆ",

    "awaiting_screening": "ಮಾದರಿ ತಪಾಸಣೆಗಾಗಿ ಕಾಯಲಾಗುತ್ತಿದೆ. ಪುಟ ೨ ರಲ್ಲಿ ಚಿತ್ರವನ್ನು ನೀಡಿ ಮತ್ತು ವಿಶ್ಲೇಷಿಸಿ ಕ್ಲಿಕ್ ಮಾಡಿ.",

    "showing_diagnosis": "ಇವರ ಸ್ವಯಂಚಾಲಿತ ತಪಾಸಣಾ ಫಲಿತಾಂಶ:",

    "analyze_another_photo": "ಮತ್ತೊಂದು ಫೋಟೋ ಪರೀಕ್ಷಿಸಿ ➔",

    "badge_suspected": "ರೋಗದ ಶಂಕೆ ಕಂಡುಬಂದಿದೆ",

    "badge_healthy": "ಆರೋಗ್ಯಕರ ಗಿಡ",

    "badge_review": "ಈ ಫೋಟೋವನ್ನು ಮತ್ತೆ ಪರಿಶೀಲಿಸಬೇಕಾಗಿದೆ.",

    "advisory_caption": "ಫೋಟೋ ಆಧಾರಿತ ಸಲಹೆ. ಗಿಡವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ತಜ್ಞರ ಸಲಹೆ ಪಡೆಯಿರಿ.",

    "score_label": "ಮಾದರಿಯ ತುಲನಾತ್ಮಕ ಅಂಕ",

    "score_sub": "ನಾಲ್ಕು ಮಾದರಿ ವರ್ಗಗಳ ತುಲನಾತ್ಮಕ ಅಂಕ. ಇದು ರೋಗ ಖಚಿತತೆಯ ಶೇಕಡಾವಾರು ಅಲ್ಲ.",

    "see_all_scores": "▴ ನಾಲ್ಕು ಮಾದರಿ ಅಂಕಗಳನ್ನು ಮರೆಮಾಡಿ",

    "see_all_scores_open": "▾ ಎಲ್ಲಾ ನಾಲ್ಕು ಮಾದರಿ ಅಂಕಗಳನ್ನು ನೋಡಿ",

    "primary_match": "ಮುಖ್ಯ ಹೊಂದಾಣಿಕೆ",

    "understanding_title": "ಈ ಫಲಿತಾಂಶವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ",

    "copy_advisory": "ಸಲಹೆ ನಕಲಿಸಿ",

    "advisory_copied": "✓ ನಕಲಿಸಲಾಗಿದೆ!",

    "influenced_title": "ಫಲಿತಾಂಶಕ್ಕೆ ಯಾವ ಭಾಗದ ಕೊಡುಗೆ ನೀಡಿದೆ?",

    "tab_model_input": "ಮಾದರಿ ಇನ್‌ಪುಟ್",

    "tab_cam_overlay": "CAM ಓವರ್‌ಲೇ",

    "tab_compare": "ಹೋಲಿಕೆ",

    "tab_curtain": "ಪರದೆ ಸ್ಲೈಡರ್ ◂▸",

    "curtain_model_input": "ಮಾದರಿ ಇನ್‌ಪುಟ್",

    "curtain_heatmap": "Grad-CAM ಹೀಟ್‌ಮ್ಯಾಪ್",

    "overlay_opacity": "ಓವರ್‌ಲೇ ಪಾರದರ್ಶಕತೆ",

    "less_contrib": "ಕಡಿಮೆ ಕೊಡುಗೆ",

    "more_contrib": "ಹೆಚ್ಚು ಕೊಡುಗೆ",

    "cam_caption": "ಕೆಂಪು ಮತ್ತು ಹಳದಿ ಬಣ್ಣಗಳು ಮಾದರಿಯು ಗಮನಿಸಿದ ಮುಖ್ಯ ಭಾಗಗಳನ್ನು ಸೂಚಿಸುತ್ತವೆ. ಅವು ರೋಗದ ನಿರ್ಣಾಯಕ ಪುರಾವೆಯಲ್ಲ.",

    "layer_tag": "ಪದರ: ResNet-50 • layer4",

    "latency_tag": "ಪ್ರತಿಕ್ರಿಯೆ ಸಮಯ:",

    "btn_scan_another": "◂ ಮತ್ತೊಂದು ಮಾದರಿ ಪರೀಕ್ಷಿಸಿ",

    "btn_turn_dossier": "ರೋಗ ಮಾಹಿತಿ ಕೋಶಕ್ಕೆ ಹೋಗಿ",

    "btn_turn_back_results": "◂ ಫಲಿತಾಂಶ & XAI ಗೆ ಹಿಂತಿರುಗಿ (ಪುಟ ೪)",

    "dossier_headline": "ಅಡಿಕೆ ಸಸ್ಯ ಆರೋಗ್ಯ ವಿಶ್ವಕೋಶ ಮತ್ತು ಕೃಷಿ ಸಲಹಾ ಕೈಪಿಡಿ",

    "dossier_lead": "ಅಡಿಕೆಯ ನಾಲ್ಕು ಮುಖ್ಯ ವರ್ಗಗಳ ಸಮಗ್ರ ಜೈವಿಕ ವಿಶ್ಲೇಷಣೆ: ರೋಗಕಾರಕಗಳು, ಹರಡುವಿಕೆ ಲಕ್ಷಣಗಳು, ICAR-CPCRI ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು ಮತ್ತು ಸಾಧಕ-ಬಾಧಕಗಳ ತುಲನೆ.",

    "tab_dossier_mahali": "🍄 ಮಹಾಲಿ / ಕೊಳೆರೋಗ (ಹಣ್ಣು ಕೊಳೆ)",

    "tab_dossier_yld": "🍂 ಹಳದಿ ಎಲೆ ರೋಗ (ವೈಎಲ್‌ಡಿ)",

    "tab_dossier_healthy_nut": "🌰 ಆರೋಗ್ಯಕರ ಅಡಿಕೆ (ನಿಯಂತ್ರಣ)",

    "tab_dossier_healthy_leaf": "🍃 ಆರೋಗ್ಯಕರ ಎಲೆ (ನಿಯಂತ್ರಣ)",

    "btn_turn_back_input": "◂ ಮಾದರಿ ಇನ್‌ಪುಟ್‌ಗೆ ಹಿಂತಿರುಗಿ",

    "btn_start_new_inspect": "ಹೊಸ ತಪಾಸಣೆ ಪ್ರಾರಂಭಿಸಿ",

    "lang_modal_title": "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",

    "lang_modal_sub": "ನಿಮಗೆ ಅನುಕೂಲಕರವಾದ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ. ಇದನ್ನು ಯಾವಾಗ ಬೇಕಾದರೂ ಬದಲಾಯಿಸಬಹುದು.",

    "btn_continue": "ಮುಂದುವರಿಯಿರಿ ➔",

    "lang_disclaimer": "ಪ್ರಾದೇಶಿಕ ಅನುವಾದಗಳು ಕರಡು ಹಂತದಲ್ಲಿವೆ. ಕೃಷಿ ಅಧಿಕಾರಿಗಳ ಸಲಹೆಯೇ ಅಂತಿಮ.",

    "history_title": "ನಿಮ್ಮ ಇತ್ತೀಚಿನ ಅವಲೋಕನಗಳು",

    "history_sub": "ಈ ಸಾಧನದಲ್ಲಿ ದಾಖಲಾದ ಇತ್ತೀಚಿನ ೮ ಪರಿಶೀಲನೆಗಳು. ಬ್ರೌಸರ್ ಡೇಟಾ ಅಳಿಸಿದರೆ ಇವು ಹೋಗುತ್ತವೆ.",

    "clear_history": "ಇತಿಹಾಸ ಅಳಿಸಿ",

    "no_history": "ಯಾವುದೇ ಇತಿಹಾಸ ದಾಖಲಾಗಿಲ್ಲ.",

    "empty_history_desc": "ದಾಖಲೆಗಳನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಉಳಿಸಲು ಅಡಿಕೆ ಎಲೆ ಅಥವಾ ಕಾಯಿಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾದಲ್ಲಿ ಸೆರೆಹಿಡಿಯಿರಿ.",

    "history_tag_healthy": "ಆರೋಗ್ಯಕರ ನಿಯಂತ್ರಣ",

    "history_tag_diseased": "ರೋಗದ ಶಂಕೆ ಕಂಡುಬಂದಿದೆ",

    "history_score_label": "ತುಲನಾತ್ಮಕ ಅಂಕ:",

    "camera_modal_title": "ಲೈವ್ ಮಾದರಿ ಕ್ಯಾಮೆರಾ ಸ್ಟುಡಿಯೋ",

    "camera_guide_label": "ಎಲೆ ಅಥವಾ ಅಡಿಕೆಯನ್ನು ವೃತ್ತದೊಳಗೆ ಇರಿಸಿ",

    "footer_slogan": "ಸ್ಥಳೀಯ AI ನೆರವು ಸಾಧನ—ಅಂತಿಮ ರೋಗನಿರ್ಣಯವಲ್ಲ.",

    "footer_methodology": "ಕಾರ್ಯವಿಧಾನ",

    "about_tag": "ಸಸ್ಯಾರೋಗ್ಯ AI ವಿಧಾನಶಾಸ್ತ್ರ",

    "about_title": "ತಾಂತ್ರಿಕ ವಿನ್ಯಾಸ ಮತ್ತು ರೋಗಶಾಸ್ತ್ರ",

    "about_desc": "ResNet-50 ತಂತ್ರಜ್ಞಾನ, Grad-CAM layer4 ವಿವರಣಾತ್ಮಕ AI ಎಂಜಿನ್ ಮತ್ತು ೪-ವರ್ಗಗಳ ಕೃಷಿ ರೋಗಶಾಸ್ತ್ರದ ಸಮಗ್ರ ವಿವರಣೆ.",

    "about_launch_btn": "ತಪಾಸಣೆ ಪ್ರಾರಂಭಿಸಿ",

    "about_guide_btn": "ಕ್ಷೇತ್ರ ಮಾರ್ಗದರ್ಶಿ ವೀಕ್ಷಿಸಿ ↗",

    "about_card1_title": "ನ್ಯೂರಲ್ ನೆಟ್‌ವರ್ಕ್ ವಾಸ್ತುಶಿಲ್ಪ",

    "about_card1_sub": "ಆಳವಾದ ವೈಶಿಷ್ಟ್ಯಗಳೊಂದಿಗೆ ಟ್ರಾನ್ಸ್‌ಫರ್ ಲರ್ನಿಂಗ್ ತಂತ್ರಜ್ಞಾನ",

    "about_card1_p1": "ArecaLens ಅಡಿಕೆ ಮರದ ಎಲೆ ಮತ್ತು ಕಾಯಿಗಳ ರೋಗ ತಪಾಸಣೆಗಾಗಿ ವಿಶೇಷವಾಗಿ ತರಬೇತಿ ನೀಡಲಾದ ResNet-50 ಮಾದರಿಯನ್ನು ಬಳಸುತ್ತದೆ.",

    "about_backbone_label": "ಬ್ಯಾಕ್‌ಬೋನ್:",

    "about_backbone_desc": "ರೆಸಿಡ್ಯೂಯಲ್ ಶಾರ್ಟ್‌ಕಟ್ ಸಂಪರ್ಕಗಳೊಂದಿಗೆ ೫೦ ಕನ್ವಲ್ಯೂಷನಲ್ ಲೇಯರ್‌ಗಳು",

    "about_head_label": "ವರ್ಗೀಕರಣ ಹೆಡ್:",

    "about_head_desc": "೪ ವರ್ಗಗಳಿಗಾಗಿ ಮಾರ್ಪಡಿಸಲಾದ ಲೀನಿಯರ್ ಲೇಯರ್ (೨೦೪೮ → ೪ ವರ್ಗಗಳು)",

    "about_tensor_label": "ಇನ್‌ಪುಟ್ ಟೆನ್ಸರ್:",

    "about_tensor_desc": "೨೨೪ × ೨೨೪ × ೩ (ImageNet ನಿಯಮಾವಳಿಗಳಂತೆ ನಾರ್ಮಲೈಸ್ ಮಾಡಿದ RGB ಚಿತ್ರ)",

    "about_xai_label": "ವಿವರಣಾತ್ಮಕತೆ (XAI):",

    "about_xai_desc": "ಅಂತಿಮ ಲೇಯರ್ (layer4, ೨೦೪೮ ಚಾನೆಲ್ಸ್) ಮೇಲೆ ಕೇಂದ್ರೀಕರಿಸಿದ Grad-CAM",

    "about_infer_label": "ವಿಶ್ಲೇಷಣಾ ವೇಗ:",

    "about_infer_desc": "torch.no_grad() ಅಡಿಯಲ್ಲಿ ಕೇವಲ ೧೦೦ ಮಿಲಿಸೆಕೆಂಡ್‌ಗಳ ಒಳಗಿನ ಕ್ಷಿಪ್ರ ತಪಾಸಣೆ",

    "about_card2_title": "ವಿವರಣಾತ್ಮಕ AI (Grad-CAM)",

    "about_card2_sub": "ಗ್ರೇಡಿಯಂಟ್-ಆಧಾರಿತ ಹೀಟ್‌ಮ್ಯಾಪ್ ವಿವರಣೆ",

    "about_card2_p1": "ರೈತರಿಗೆ ಪಾರದರ್ಶಕತೆ ನೀಡಲು, ಮಾದರಿಯು ಅಂತಿಮ ಕನ್ವಲ್ಯೂಷನಲ್ ಲೇಯರ್‌ನ ಗ್ರೇಡಿಯಂಟ್‌ಗಳನ್ನು ಲೆಕ್ಕಹಾಕಿ ಗಮನ ಕೇಂದ್ರೀಕರಿಸಿದ ಜಾಗವನ್ನು ತೋರಿಸುತ್ತದೆ:",

    "about_card2_p2": "ReLU ವಿಧಾನವು ರೋಗಲಕ್ಷಣಕ್ಕೆ ಕಾರಣವಾದ ನಿರ್ದಿಷ್ಟ ಅಂಶಗಳನ್ನು ಗುರುತಿಸಿ, ಮೂಲ ಫೋಟೋದ ಮೇಲೆ ಹೀಟ್‌ಮ್ಯಾಪ್ ಆಗಿ ಪ್ರದರ್ಶಿಸುತ್ತದೆ.",

    "about_tax_title": "೪-ವರ್ಗಗಳ ರೋಗ ವರ್ಗೀಕರಣ",

    "about_tax_sub": "ಕೃಷಿ ಲಕ್ಷಣಗಳು, ರೋಗಕಾರಕಗಳು ಮತ್ತು ನಿರ್ವಹಣಾ ಮಾನದಂಡಗಳು",

    "status_healthy": "ಆರೋಗ್ಯಕರ",

    "status_diseased": "ರೋಗಬಾಧಿತ",

    "recom_action_label": "ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ:",

    "desc_healthy_nut": "ಯಾವುದೇ ಕಲೆಗಳಿಲ್ಲದ, ಸಮರೂಪದ ಬಣ್ಣ ಮತ್ತು ಗಟ್ಟಿಯಾದ ಕಾಯಿಯ ಲಕ್ಷಣಗಳನ್ನು ಹೊಂದಿರುವ ಆರೋಗ್ಯಕರ ಅಡಿಕೆ.",

    "mgmt_healthy_nut": "ನಿಯಮಿತ ನೀರಾವರಿ, ಸಮತೋಲಿತ ಪೋಷಕಾಂಶಗಳು (NPK) ಮತ್ತು ನಿಯಮಿತ ತಪಾಸಣೆಯನ್ನು ಮುಂದುವರಿಸಿ.",

    "desc_healthy_leaf": "ಯಾವುದೇ ಹಳದಿ ಅಥವಾ ಕಂದು ಕಲೆಗಳಿಲ್ಲದ, ಸಮೃದ್ಧ ಹಸಿರಿನಿಂದ ಕೂಡಿದ ಆರೋಗ್ಯಕರ ಅಡಿಕೆ ಗರಿ.",

    "mgmt_healthy_leaf": "ಸಾಮಾನ್ಯ ಕೃಷಿ ಪದ್ಧತಿ ಮುಂದುವರಿಸಿ; ಮಳೆಗಾಲದಲ್ಲಿ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಿಸಿ.",

    "desc_mahali": "Phytophthora meadii ಶಿಲೀಂಧ್ರದಿಂದ ಉಂಟಾಗುವ ತೀವ್ರ ಕೊಳೆರೋಗ; ಕಾಯಿಗಳು ಕೊಳೆತು ತೀವ್ರವಾಗಿ ಉದುರುತ್ತವೆ.",

    "mgmt_mahali": "ಮಳೆಗಾಲ ಆರಂಭಕ್ಕೆ ಮುನ್ನ ೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ; ೪೦-೪೫ ದಿನಗಳ ನಂತರ ಪುನರಾವರ್ತಿಸಿ. ಗೊನೆಗಳಿಗೆ ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟಿ.",

    "desc_yellow_leaf_disease": "ಫೈಟೋಪ್ಲಾಸ್ಮಾ ಸೂಕ್ಷ್ಮಾಣುವಿನಿಂದ ಉಂಟಾಗುವ ಹಳದಿ ರೋಗ; ಗರಿಗಳು ಹಳದಿಯಾಗಿ ಮರದ ಕಿರೀಟ ಕಿರಿದಾಗುತ್ತದೆ.",

    "mgmt_yellow_leaf_disease": "ಸಮತೋಲಿತ NPK ಜೊತೆಗೆ ಮ್ಯಾಗ್ನೀಸಿಯಮ್ ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರ ನೀಡಿ. ಬಸಿಗಾಲುವೆ ಸುಧಾರಿಸಿ ಮತ್ತು ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ."

  },

  "hi": {

    "lang_name": "हिन्दी",

    "brand_tagline": "आपका पौधा स्वास्थ्य साथी",

    "nav_analyze": "जाँच करें",

    "nav_guide": "रोग जानकारी",

    "nav_history": "इतिहास",
    "nav_architecture": "संरचना (Architecture)",

    "sound_label": "ध्वनि",

    "sound_muted": "म्यूट",

    "model_ready": "मॉडल तैयार है",

    "modal_badge": "अरेकालेंस",

    "step_welcome": "स्वागत",

    "step_input": "नमूना इनपुट",

    "step_analyzing": "विश्लेषण हड",

    "step_results": "परिणाम & XAI",

    "step_dossier": "रोग विवरण",

    "vol_chap_1": "खण्ड १ • अध्याय १",

    "vol_chap_2": "खण्ड १ • अध्याय २",

    "vol_chap_3": "खण्ड १ • अध्याय ३",

    "vol_chap_4": "खण्ड १ • अध्याय ४",

    "vol_chap_5": "खण्ड १ • अध्याय ५",

    "page_1_of_5": "पृष्ठ १/५",

    "page_2_of_5": "पृष्ठ २/५",

    "page_3_of_5": "पृष्ठ ३/५",

    "page_4_of_5": "पृष्ठ ४/५",

    "page_5_of_5": "पृष्ठ ५/५",

    "hero_tag": "एआई-संचालित पादप स्वास्थ्य निदान • ResNet-50",

    "hero_title": "अपनी सुपारी की देखभाल करें। जो देखें उसे स्पष्ट समझें।",
    "hero_split_eyebrow": "उगाने वालों के लिए",
    "hero_split_title": "अपनी सुपारी की<br>देखभाल करें।<br>जो देखें उसे स्पष्ट<br>समझें।",
    "hero_split_desc": "पत्ती या सुपारी की तस्वीर लें। स्क्रीनिंग सुझाव प्राप्त करें, देखें कि एआई ने क्या पहचाना, और जानें कि आगे क्या जाँचना है।",
    "btn_get_started": "शुरू करें",
    "hero_flow_label": "फोटो → स्क्रीनिंग → स्पष्टीकरण",
    "lang_pane_tag": "चरण १ • इंटरफ़ेस भाषा का चयन करें",
    "lang_pane_title": "अपनी भाषा चुनें",
    "lang_pane_sub": "अपनी पसंदीदा भाषा चुनें। एआई निदान और कृषि देखभाल दिशानिर्देश आपके लिए इस भाषा में उपलब्ध होंगे।",
    "btn_continue_inspect": "नमूना इनपुट के लिए आगे बढ़ें",
    "btn_back": "वापस",

    "hero_desc": "सुपारी की खेती के लिए निर्मित इंटरैक्टिव पृष्ठ-दर-पृष्ठ नैदानिक ​​विश्वकोश। ५०-परतों वाले डीप रेजिड्यूअल विज़न, Grad-CAM व्याख्यात्मक एआई (XAI) और प्रमाणित ICAR-CPCRI कृषि देखभाल प्रोटोकॉल का समन्वय।",

    "feat_classes_title": "४ रोग वर्ग",

    "feat_classes_desc": "स्वस्थ पत्ता, स्वस्थ सुपारी, महाली फल सड़न, पीला पत्ता रोग।",

    "feat_layers_title": "५० रेजिड्यूअल लेयर्स",

    "feat_layers_desc": "उच्च-रिज़ॉल्यूशन वाले फील्ड नमूनों पर प्रशिक्षित डीप बॉटलनैक फीचर एक्सट्रैक्शन।",

    "feat_xai_title": "व्याख्यात्मक एआई (XAI)",

    "feat_xai_desc": "रीयल-टाइम Grad-CAM हीटमैप विश्लेषण किए गए सटीक पत्ती और फल के हिस्सों को उजागर करते हैं।",

    "feat_edge_title": "१००% स्थानीय प्रोसेसिंग",

    "feat_edge_desc": "कोई तृतीय-पक्ष एपीआई नहीं। पूरी तरह निजी, सुरक्षित और सीधे इसी सर्वर पर निष्पादित।",

    "btn_start_inspect": "जाँच शुरू करें",

    "btn_browse_dossier": "रोग विवरण देखें",

    "upload_card_title": "पौधे की फोटो जोड़ें",

    "upload_sub": "फोटो अपलोड करें या लाइव कैमरे से लें",

    "upload_card_tag": "पत्ता या फल",

    "dropzone_title": "साफ़ फोटो बेहतर जानकारी देती है।",

    "dropzone_sub": "फोटो यहाँ छोड़ें या नीचे दिए गए विकल्प चुनें।",

    "btn_choose_image": "फोटो चुनें",

    "btn_use_camera": "कैमरा इस्तेमाल करें",

    "dropzone_formats": "JPG, JPEG या PNG • अधिकतम 10MB",

    "change_photo": "फोटो बदलें",

    "samples_heading": "⚡ त्वरित परीक्षण नमूने (नमूना लोड करने के लिए क्लिक करें):",

    "sample_healthy_leaf": "🍃 स्वस्थ पत्ता",

    "sample_healthy_nut": "🌰 स्वस्थ सुपारी",

    "sample_mahali": "🍄 महाली सड़न",

    "sample_yld": "🍂 पीला पत्ता",

    "btn_analyze": "पौधे की जाँच करें ↗",

    "btn_analyzing": "फोटो की जाँच हो रही है...",

    "tips_card_title": "साफ़ फोटो बेहतर जानकारी देती है।",

    "tips_card_sub": "साफ़ दृश्य मॉडल को सटीक जाँच में मदद करता है। हाथों से पौधे को न ढकें और अधिक व्यस्त पृष्ठभूमि से बचें।",

    "tip_1_title": "प्राकृतिक रोशनी में लें",

    "tip_1_desc": "दिन की प्राकृतिक रोशनी भ्रामक छाया से बचाती है।",

    "tip_2_title": "फ्रेम में एक पत्ता या फल रखें",

    "tip_2_desc": "प्रभावित हिस्से के इतने नज़दीक जाएँ कि वह स्पष्ट दिखे।",

    "tip_3_title": "कैमरा स्थिर रखें",

    "tip_3_desc": "स्पष्ट फोकस धुंधलेपन को नैदानिक ​​संकेतों को बिगाड़ने से रोकता है।",

    "tips_disclaimer": "फोटो जाँच अंतिम नहीं है। कृषि विशेषज्ञ की पुष्टि आवश्यक है।",

    "btn_turn_back_welcome": "◂ स्वागत पृष्ठ पर वापस जाएँ",

    "btn_run_screening": "स्क्रीनिंग और XAI विश्लेषण चलाएँ",

    "hud_headline": "नमूने की जाँच और Grad-CAM की गणना जारी है...",

    "hud_caption": "५०-स्तरीय डीप रेजिड्यूअल इन्फेरेंस और Grad-CAM हीटमैप तैयार किया जा रहा है।",

    "phase_1_text": "[१] नमूना ग्रहण और 224x224 RGB टेन्सर सामान्यीकरण",

    "phase_2_text": "[२] ५० रेसनेट ब्लॉक्स में २०४८-आयामी विशेषताओं का निष्कर्षण",

    "phase_3_text": "[३] layer4 बॉटलनैक पर Grad-CAM ग्रेडिएंट बैकप्रॉपैगैशन",

    "phase_4_text": "[४] ICAR-CPCRI कृषि सलाह और रोग विवरण संकलन",

    "awaiting_screening": "नमूना जाँच की प्रतीक्षा है। पृष्ठ २ पर चित्र अपलोड करें और विश्लेषण करें पर क्लिक करें।",

    "showing_diagnosis": "का स्वचालित स्क्रीनिंग परिणाम:",

    "analyze_another_photo": "दूसरी फोटो की जाँच करें ➔",

    "badge_suspected": "रोग का संदेह",

    "badge_healthy": "स्वस्थ पौधा",

    "badge_review": "इस फोटो को दोबारा जाँचने की आवश्यकता है।",

    "advisory_caption": "फोटो के आधार पर सुझाव। पौधे की जाँच करें और कृषि विशेषज्ञ की राय लें।",

    "score_label": "मॉडल का तुलनात्मक अंक",

    "score_sub": "चारों मॉडल वर्गों का तुलनात्मक अंक। यह सटीक निदान की गारंटी नहीं है।",

    "see_all_scores": "▴ चारों मॉडल स्कोर छुपाएँ",

    "see_all_scores_open": "▾ सभी चार मॉडल स्कोर देखें",

    "primary_match": "प्राथमिक मेल",

    "understanding_title": "इस परिणाम को समझें",

    "copy_advisory": "सलाह कॉपी करें",

    "advisory_copied": "✓ कॉपी हो गया!",

    "influenced_title": "परिणाम में किस हिस्से ने योगदान दिया?",

    "tab_model_input": "मॉडल इनपुट",

    "tab_cam_overlay": "CAM ओवरले",

    "tab_compare": "तुलना",

    "tab_curtain": "पर्दा स्लाइडर ◂▸",

    "curtain_model_input": "मॉडल इनपुट",

    "curtain_heatmap": "Grad-CAM हीटमैप",

    "overlay_opacity": "ओवरले पारदर्शिता",

    "less_contrib": "कम प्रभाव",

    "more_contrib": "अधिक प्रभाव",

    "cam_caption": "गर्म रंग (लाल/पीला) मॉडल द्वारा पहचाने गए मुख्य हिस्सों को दर्शाते हैं। वे रोग की पुष्टि नहीं करते।",

    "layer_tag": "लेयर: ResNet-50 • layer4",

    "latency_tag": "प्रतिक्रिया समय:",

    "btn_scan_another": "◂ दूसरा नमूना जाँचें",

    "btn_turn_dossier": "रोग विवरण पर जाएँ",

    "btn_turn_back_results": "◂ परिणाम & XAI पर वापस जाएँ (पृष्ठ ४)",

    "dossier_headline": "सुपारी पादप स्वास्थ्य विश्वकोश एवं कृषि परामर्श निर्देशिका",

    "dossier_lead": "सुपारी के चारों प्रमुख वर्गों का संपूर्ण जैविक विश्लेषण: रोगजनक, लक्षण प्रगति, ICAR-CPCRI प्रबंधन प्रोटोकॉल और रणनीतिक तुलना।",

    "tab_dossier_mahali": "🍄 महाली / कोलेरोगा (फल सड़न)",

    "tab_dossier_yld": "🍂 पीला पत्ता रोग (वाईएलडी)",

    "tab_dossier_healthy_nut": "🌰 स्वस्थ सुपारी (नियंत्रण)",

    "tab_dossier_healthy_leaf": "🍃 स्वस्थ पत्ता (नियंत्रण)",

    "btn_turn_back_input": "◂ नमूना इनपुट पर वापस जाएँ",

    "btn_start_new_inspect": "नई जाँच शुरू करें",

    "lang_modal_title": "अपनी भाषा चुनें",

    "lang_modal_sub": "जिस भाषा में आप सहज हैं, उसे चुनें। आप इसे कभी भी बदल सकते हैं।",

    "btn_continue": "आगे बढ़ें ➔",

    "lang_disclaimer": "क्षेत्रीय अनुवाद प्राथमिक हैं। कृषि अधिकारियों की सलाह सर्वोपरि है।",

    "history_title": "आपके हाल के अवलोकन",

    "history_sub": "इस डिवाइस पर सहेजे गए पिछले ८ स्कैन। ब्राउज़र डेटा साफ़ करने पर ये हट जाएँगे।",

    "clear_history": "इतिहास साफ़ करें",

    "no_history": "अभी कोई स्कैन इतिहास दर्ज नहीं है।",

    "empty_history_desc": "निदान रिकॉर्ड सहेजने के लिए सुपारी के पत्ते या फल की फोटो अपलोड करें या कैमरे से लें।",

    "history_tag_healthy": "स्वस्थ नियंत्रण",

    "history_tag_diseased": "रोग का संदेह",

    "history_score_label": "तुलनात्मक अंक:",

    "camera_modal_title": "लाइव नमूना कैमरा स्टूडियो",

    "camera_guide_label": "पत्ते या सुपारी को घेरे के अंदर रखें",

    "footer_slogan": "स्थानीय AI सहायता उपकरण—अंतिम निदान नहीं।",

    "footer_methodology": "कार्यप्रणाली",

    "about_tag": "पादप स्वास्थ्य AI कार्यप्रणाली",

    "about_title": "तकनीकी वास्तुकला एवं रोगविज्ञान",

    "about_desc": "ट्रांसफर-लर्नड ResNet-50 आर्किटेक्चर, Grad-CAM layer4 व्याख्यात्मक AI इंजन और 4-श्रेणी कृषि रोग वर्गीकरण का विवरण।",

    "about_launch_btn": "जांच शुरू करें",

    "about_guide_btn": "फील्ड गाइड देखें ↗",

    "about_card1_title": "न्यूरल नेटवर्क आर्किटेक्चर",

    "about_card1_sub": "गहन अवशिष्ट फीचर निरूपण के साथ ट्रांसफर लर्निंग",

    "about_card1_p1": "ArecaLens सुपारी के पत्ते और फल रोगों की पहचान के लिए विशेष रूप से प्रशिक्षित ResNet-50 मॉडल का उपयोग करता है।",

    "about_backbone_label": "बैकबोन:",

    "about_backbone_desc": "रेसिड्यूअल शॉर्टकट कनेक्शन के साथ 50 दृढ़ कनवल्शनल लेयर्स",

    "about_head_label": "वर्गीकरण हेड:",

    "about_head_desc": "4 वर्गों के लिए अनुकूलित लीनियर लेयर (2048 → 4 वर्ग)",

    "about_tensor_label": "इनपुट टेंसर:",

    "about_tensor_desc": "224 × 224 × 3 (ImageNet मानकों पर सामान्यीकृत RGB छवि)",

    "about_xai_label": "व्याख्यात्मकता (XAI):",

    "about_xai_desc": "अंतिम लेयर (layer4, 2048 चैनल्स) पर लक्षित Grad-CAM",

    "about_infer_label": "अनुमान गति:",

    "about_infer_desc": "torch.no_grad() के अंतर्गत 100 मिलीसेकंड से कम में त्वरित परिणाम",

    "about_card2_title": "व्याख्यात्मक AI (Grad-CAM)",

    "about_card2_sub": "ग्रेडिएंट-आधारित हीटमैप विज़ुअलाइज़ेशन",

    "about_card2_p1": "किसानों को पारदर्शिता प्रदान करने के लिए, मॉडल अंतिम कनवल्शनल लेयर के ग्रेडिएंट्स की गणना करके दिखाता है कि उसने कहाँ देखा:",

    "about_card2_p2": "ReLU तकनीक रोग के सकारात्मक लक्षणों को अलग करती है और मूल फोटो पर हीटमैप के रूप में प्रदर्शित करती है।",

    "about_tax_title": "4-श्रेणी रोग वर्गीकरण",

    "about_tax_sub": "कृषि विशेषताएँ, रोगकारक और प्रबंधन मानक",

    "status_healthy": "स्वस्थ",

    "status_diseased": "रोगग्रस्त",

    "recom_action_label": "अनुशंसित कार्रवाई:",

    "desc_healthy_nut": "बिना किसी कवक धब्बे के, एकसमान रंग और ठोस आंतरिक गिरी वाली स्वस्थ सुपारी।",

    "mgmt_healthy_nut": "नियमित सिंचाई, संतुलित पोषण (NPK) और नियमित वृक्ष निरीक्षण जारी रखें।",

    "desc_healthy_leaf": "बिना किसी पीलेपन या सड़न के, चमकदार हरी और मजबूत सुपारी की पत्ती।",

    "mgmt_healthy_leaf": "उचित जल निकासी बनाए रखें और मानसून में जड़ों के पास पानी जमा न होने दें।",

    "desc_mahali": "Phytophthora meadii कवक द्वारा जनित महाली/कोलेरोगा; फल सड़कर भारी संख्या में गिरते हैं।",

    "mgmt_mahali": "मानसून से पूर्व 1% बोर्डो मिश्रण का छिड़काव करें; 40-45 दिन बाद दोहराएँ। गुच्छों पर पॉलिथीन बाँधें।",

    "desc_yellow_leaf_disease": "फाइटोप्लाज्मा द्वारा जनित पीली पत्ती रोग (YLD); पत्तियाँ पीली होकर सूखती हैं और उपज घटती है।",

    "mgmt_yellow_leaf_disease": "संतुलित NPK के साथ मैग्नीशियम और जैविक खाद दें। जल निकासी सुधारें।"

  },

  "ml": {

    "lang_name": "മലയാളം",

    "brand_tagline": "നിങ്ങളുടെ സസ്യാരോഗ്യ സഹായി",

    "nav_analyze": "പരിശോധിക്കുക",

    "nav_guide": "രോഗവിവരങ്ങൾ",

    "nav_history": "ചരിത്രം",

    "sound_label": "ശബ്ദം",

    "sound_muted": "നിശബ്ദം",

    "model_ready": "മോഡൽ തയ്യാറാണ്",

    "modal_badge": "അടക്കലെൻസ്",

    "step_welcome": "സ്വാഗതം",

    "step_input": "മാതൃക ഇൻപുട്ട്",

    "step_analyzing": "വിശകലന ഹഡ്",

    "step_results": "ഫലങ്ങൾ & XAI",

    "step_dossier": "രോഗവിവരശേഖരം",

    "vol_chap_1": "വോള്യം 1 • അധ്യായം 1",

    "vol_chap_2": "വോള്യം 1 • അധ്യായം 2",

    "vol_chap_3": "വോള്യം 1 • അധ്യായം 3",

    "vol_chap_4": "വോള്യം 1 • അധ്യായം 4",

    "vol_chap_5": "വോള്യം 1 • അധ്യായം 5",

    "page_1_of_5": "പേജ് 1/5",

    "page_2_of_5": "പേജ് 2/5",

    "page_3_of_5": "പേജ് 3/5",

    "page_4_of_5": "പേജ് 4/5",

    "page_5_of_5": "പേജ് 5/5",

    "hero_tag": "എഐ അധിഷ്ഠിത സസ്യരോഗ നിർണ്ണയം • ResNet-50",

    "hero_title": "നിങ്ങളുടെ അടക്കത്തോട്ടം സംരക്ഷിക്കുക. കാണുന്ന ലക്ഷണങ്ങൾ തിരിച്ചറിയുക.",
    "hero_split_eyebrow": "കർഷകർക്കായി",
    "hero_split_title": "നിങ്ങളുടെ അടക്കത്തോട്ടം<br>സംരക്ഷിക്കുക.<br>ലക്ഷണങ്ങൾ വ്യക്തമായി<br>മനസ്സിലാക്കുക.",
    "hero_split_desc": "ഇലയുടെയോ അടക്കയുടെയോ ഫോട്ടോ എടുക്കുക. സ്‌ക്രീനിംഗ് നിർദ്ദേശങ്ങൾ നേടുക, എഐ കണ്ടെത്തിയത് കാണുക, അടുത്തതായി എന്താണ് ചെയ്യേണ്ടതെന്ന് മനസ്സിലാക്കുക.",
    "btn_get_started": "ആരംഭിക്കുക",
    "hero_flow_label": "ഫോട്ടോ → സ്ക്രീനിംഗ് → വിശദീകരണം",
    "lang_pane_tag": "ഘട്ടം 1 • ഇന്റർഫേസ് ഭാഷ തിരഞ്ഞെടുക്കുക",
    "lang_pane_title": "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
    "lang_pane_sub": "നിങ്ങൾക്ക് സൗകര്യപ്രദമായ ഭാഷ തിരഞ്ഞെടുക്കുക. എഐ രോഗനിർണ്ണയവും പരിചരണ മാർഗ്ഗനിർദ്ദേശങ്ങളും ഈ ഭാഷയിൽ ലഭ്യമാകും.",
    "btn_continue_inspect": "തുടരുക",
    "btn_back": "തിരികെ",

    "hero_desc": "അടക്ക കൃഷിക്കായി രൂപകൽപ്പന ചെയ്ത ഇന്ററാക്ടീവ് സസ്യരോഗ വിജ്ഞാനകോശം. 50-ലെയർ ഡീപ് റെസിഡ്യൂവൽ വിഷൻ, Grad-CAM വിശദീകരണ എഐ (XAI), ICAR-CPCRI കാർഷിക പരിചരണ മാർഗ്ഗനിർദ്ദേശങ്ങൾ എന്നിവ സംയോജിപ്പിച്ചത്.",

    "feat_classes_title": "4 രോഗ വിഭാഗങ്ങൾ",

    "feat_classes_desc": "ആരോഗ്യമുള്ള ഇല, ആരോഗ്യമുള്ള അടക്ക, മഹാലി കായ്ചീയൽ, മഞ്ഞളിപ്പ് രോഗം.",

    "feat_layers_title": "50 റെസിഡ്യൂവൽ ലെയറുകൾ",

    "feat_layers_desc": "ഉയർന്ന റെസല്യൂഷൻ തോട്ടം മാതൃകകളിൽ പരിശീലിപ്പിച്ച ആഴത്തിലുള്ള ഫീച്ചർ വിശകലനം.",

    "feat_xai_title": "വിശദീകരണ എഐ (XAI)",

    "feat_xai_desc": "തത്സമയ Grad-CAM ഹീറ്റ്മാപ്പുകൾ വിശകലനം ചെയ്ത ഇലയുടെയും അടക്കയുടെയും ഭാഗങ്ങൾ കൃത്യമായി വ്യക്തമാക്കുന്നു.",

    "feat_edge_title": "100% പ്രാദേശിക പ്രോസസ്സിംഗ്",

    "feat_edge_desc": "ബാഹ്യ എപിഐകൾ ഒന്നുമില്ല. സുരക്ഷിതവും പൂർണ്ണമായും ഈ സെർവറിൽ തന്നെ പ്രവർത്തിക്കുന്നതും.",

    "btn_start_inspect": "പരിശോധന ആരംഭിക്കുക",

    "btn_browse_dossier": "രോഗ വിവരങ്ങൾ കാണുക",

    "upload_card_title": "ചെടിയുടെ ചിത്രം ചേർക്കുക",

    "upload_sub": "ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുകയോ ലൈവ് ക്യാമറ ഉപയോഗിക്കുകയോ ചെയ്യുക",

    "upload_card_tag": "ഇല അല്ലെങ്കിൽ അടക്ക",

    "dropzone_title": "വ്യക്തമായ ചിത്രം നല്ല വിവരങ്ങൾക്ക് സഹായിക്കും.",

    "dropzone_sub": "ഫോട്ടോ ഇവിടെ ഇടുക അല്ലെങ്കിൽ താഴെയുള്ളവ തിരഞ്ഞെടുക്കുക.",

    "btn_choose_image": "ഫോട്ടോ തിരഞ്ഞെടുക്കുക",

    "btn_use_camera": "ക്യാമറ ഉപയോഗിക്കുക",

    "dropzone_formats": "JPG, JPEG അല്ലെങ്കിൽ PNG • പരമാവധി 10MB",

    "change_photo": "ഫോട്ടോ മാറ്റുക",

    "samples_heading": "⚡ തൽക്ഷണ പരിശോധനാ മാതൃകകൾ (മാതൃക കാണാൻ ക്ലിക്ക് ചെയ്യുക):",

    "sample_healthy_leaf": "🍃 ആരോഗ്യമുള്ള ഇല",

    "sample_healthy_nut": "🌰 ആരോഗ്യമുള്ള അടക്ക",

    "sample_mahali": "🍄 മഹാലി ചീയൽ",

    "sample_yld": "🍂 മഞ്ഞളിപ്പ്",

    "btn_analyze": "ചെടിയുടെ ആരോഗ്യം പരിശോധിക്കുക ↗",

    "btn_analyzing": "ഫോട്ടോ പരിശോധിക്കുന്നു...",

    "tips_card_title": "വ്യക്തമായ ചിത്രം നല്ല വിവരങ്ങൾ നൽകും.",

    "tips_card_sub": "വ്യക്തമായ ചിത്രം മോഡലിന് കൃത്യമായ വിശകലനം സാധ്യമാക്കുന്നു. കൈകൾ മറയ്ക്കാതിരിക്കാനും അനാവശ്യ പശ്ചാത്തലം ഒഴിവാക്കാനും ശ്രദ്ധിക്കുക.",

    "tip_1_title": "സ്വാഭാവിക വെളിച്ചത്തിൽ എടുക്കുക",

    "tip_1_desc": "പകൽ വെളിച്ചം അനാവശ്യ നിഴലുകൾ ഒഴിവാക്കാൻ സഹായിക്കും.",

    "tip_2_title": "ഒരു ഇലയോ കായയോ വ്യക്തമായി കാണിക്കുക",

    "tip_2_desc": "ലക്ഷണമുള്ള ഭാഗം വലുതായി കാണുന്ന വിധം അടുത്ത് നിന്ന് എടുക്കുക.",

    "tip_3_title": "ക്യാമറ അനങ്ങാതെ പിടിക്കുക",

    "tip_3_desc": "വ്യക്തമായ ചിത്രം തെറ്റായ നിഗമനം ഒഴിവാക്കാൻ സഹായിക്കും.",

    "tips_disclaimer": "ഫോട്ടോ പരിശോധന അന്തിമമല്ല. കൃഷി വിദഗ്ദ്ധരുടെ ഉപദേശം തേടുക.",

    "btn_turn_back_welcome": "◂ സ്വാഗത പേജിലേക്ക് മടങ്ങുക",

    "btn_run_screening": "സ്ക്രീനിംഗും XAI വിശകലനവും നടത്തുക",

    "hud_headline": "മാതൃക സ്കാൻ ചെയ്യുകയും Grad-CAM കണക്കാക്കുകയും ചെയ്യുന്നു...",

    "hud_caption": "50-ലെയർ ഡീപ് റെസിഡ്യൂവൽ ഇൻഫറൻസും Grad-CAM ഹീറ്റ്മാപ്പും തയ്യാറാക്കുന്നു.",

    "phase_1_text": "[1] മാതൃക സ്വീകരിക്കലും 224x224 RGB ടെൻസർ ക്രമീകരിക്കലും",

    "phase_2_text": "[2] 50 റെസ്നെറ്റ് ബ്ലോക്കുകളിൽ 2048-ഡൈമൻഷൻ വിശകലനം",

    "phase_3_text": "[3] layer4 ബോട്ടിൽനെക്കിൽ Grad-CAM ഗ്രേഡിയന്റ് വിശകലനം",

    "phase_4_text": "[4] ICAR-CPCRI കാർഷിക നിർദ്ദേശങ്ങളും വിവരങ്ങളും സമാഹരിക്കുന്നു",

    "awaiting_screening": "പരിശോധനയ്ക്കായി കാത്തിരിക്കുന്നു. പേജ് 2-ൽ ചിത്രം നൽകി വിശകലനം ക്ലിക്ക് ചെയ്യുക.",

    "showing_diagnosis": "ഇതിന്റെ സ്വയമേവയുള്ള പരിശോധനാ ഫലം:",

    "analyze_another_photo": "മറ്റൊരു ഫോട്ടോ പരിശോധിക്കുക ➔",

    "badge_suspected": "രോഗലക്ഷണം സംശയിക്കുന്നു",

    "badge_healthy": "ആരോഗ്യമുള്ള ചെടി",

    "badge_review": "ഈ ഫോട്ടോ വീണ്ടും പരിശോധിക്കേണ്ടതുണ്ട്.",

    "advisory_caption": "ചിത്രത്തിൽ നിന്നുള്ള പ്രാഥമിക നിഗമനം. കൃഷി വിദഗ്ദ്ധരുടെ ഉപദേശം തേടുക.",

    "score_label": "മോഡലിന്റെ താരതമ്യ സ്കോർ",

    "score_sub": "നാല് മോഡൽ വിഭാഗങ്ങൾ തമ്മിലുള്ള താരതമ്യ സ്കോർ. ഇത് കൃത്യമായ രോഗനിർണ്ണയമല്ല.",

    "see_all_scores": "▴ നാല് മോഡൽ സ്കോറുകൾ മറയ്ക്കുക",

    "see_all_scores_open": "▾ നാല് മോഡൽ സ്കോറുകളും കാണുക",

    "primary_match": "പ്രധാന പൊരുത്തം",

    "understanding_title": "ഈ ഫലം മനസ്സിലാക്കാം",

    "copy_advisory": "നിർദ്ദേശം പകർത്തുക",

    "advisory_copied": "✓ പകർത്തി!",

    "influenced_title": "ഏത് ഭാഗമാണ് സ്വാധീനം നൽകിയത്?",

    "tab_model_input": "മോഡൽ ഇൻപുട്ട്",

    "tab_cam_overlay": "CAM ഓവർലേ",

    "tab_compare": "താരതമ്യം",

    "tab_curtain": "കർട്ടൻ സ്ലൈഡർ ◂▸",

    "curtain_model_input": "മോഡൽ ഇൻപുട്ട്",

    "curtain_heatmap": "Grad-CAM ഹീറ്റ്മാപ്പ്",

    "overlay_opacity": "ഓവർലേ അതാര്യത",

    "less_contrib": "കുറഞ്ഞ സ്വാധീനം",

    "more_contrib": "കൂടുതൽ സ്വാധീനം",

    "cam_caption": "ചുവപ്പ്/മഞ്ഞ നിറങ്ങൾ മോഡൽ വിശകലനം ചെയ്ത പ്രധാന ഭാഗങ്ങളെ കാണിക്കുന്നു. ഇത് രോഗത്തിന്റെ അന്തിമ സ്ഥിരീകരണമല്ല.",

    "layer_tag": "ലെയർ: ResNet-50 • layer4",

    "latency_tag": "പ്രതികരണ സമയം:",

    "btn_scan_another": "◂ മറ്റൊരു മാതൃക പരിശോധിക്കുക",

    "btn_turn_dossier": "രോഗ വിവരങ്ങളിലേക്ക് പോകുക",

    "btn_turn_back_results": "◂ ഫലങ്ങൾ & XAI-ലേക്ക് മടങ്ങുക (പേജ് 4)",

    "dossier_headline": "അടക്ക സസ്യാരോഗ്യ വിജ്ഞാനകോശവും കാർഷിക നിർദ്ദേശാവലിയും",

    "dossier_lead": "അടക്കയിലെ നാല് പ്രധാന വിഭാഗങ്ങളുടെ സമഗ്ര ജൈവിക വിശകലനം: രോഗകാരികൾ, ലക്ഷണങ്ങൾ, ICAR-CPCRI പരിചരണ നിർദ്ദേശങ്ങൾ, ഗുണദോഷ താരതമ്യം.",

    "tab_dossier_mahali": "🍄 മഹാലി / കൊളെറോഗ (കായ്ചീയൽ)",

    "tab_dossier_yld": "🍂 മഞ്ഞളിപ്പ് രോഗം (വൈഎൽഡി)",

    "tab_dossier_healthy_nut": "🌰 ആരോഗ്യമുള്ള അടക്ക (നിയന്ത്രണം)",

    "tab_dossier_healthy_leaf": "🍃 ആരോഗ്യമുള്ള ഇല (നിയന്ത്രണം)",

    "btn_turn_back_input": "◂ മാതൃക ഇൻപുട്ടിലേക്ക് മടങ്ങുക",

    "btn_start_new_inspect": "പുതിയ പരിശോധന ആരംഭിക്കുക",

    "lang_modal_title": "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",

    "lang_modal_sub": "നിങ്ങൾക്ക് സൗകര്യപ്രദമായ ഭാഷ തിരഞ്ഞെടുക്കുക. ഇത് നിങ്ങൾക്ക് എപ്പോൾ വേണമെങ്കിലും മാറ്റാം.",

    "btn_continue": "തുടരുക ➔",

    "lang_disclaimer": "പ്രാദേശിക വിവർത്തനങ്ങൾ പ്രാഥമികമാണ്. കൃഷി ഓഫീസർമാരുടെ ഉപദേശം അന്തിമമാണ്.",

    "history_title": "നിങ്ങളുടെ സമീപകാല നിരീക്ഷണങ്ങൾ",

    "history_sub": "ഈ ഉപകരണത്തിൽ രേഖപ്പെടുത്തിയ അവസാന ൮ പരിശോധനകൾ. ബ്രൗസർ ഡാറ്റ മായ്ച്ചാൽ ഇവ നഷ്ടപ്പെടും.",

    "clear_history": "ഹിസ്റ്ററി ഒഴിവാക്കുക",

    "no_history": "ഇതുവരെ സ്കാനുകളൊന്നും രേഖപ്പെടുത്തിയിട്ടില്ല.",

    "empty_history_desc": "രേഖകൾ സ്വയമേവ സൂക്ഷിക്കാൻ അടക്കയിലയോ കായയോ ഫോട്ടോ എടുക്കുകയോ അപ്‌ലോഡ് ചെയ്യുകയോ ചെയ്യുക.",

    "history_tag_healthy": "ആരോഗ്യമുള്ള നിയന്ത്രണം",

    "history_tag_diseased": "രോഗലക്ഷണം സംശയിക്കുന്നു",

    "history_score_label": "താരതമ്യ സ്കോർ:",

    "camera_modal_title": "തത്സമയ മാതൃകാ ക്യാമറ സ്റ്റുഡിയോ",

    "camera_guide_label": "ഇലയോ അടക്കയോ വൃത്തത്തിനുള്ളിൽ ക്രമീകരിക്കുക",

    "footer_slogan": "പ്രാദേശിക AI സഹായ ഉപകരണം—അന്തിമ രോഗനിർണ്ണയമല്ല.",

    "footer_methodology": "പ്രവർത്തനരീതി",

    "about_tag": "സസ്യാരോഗ്യ AI രീതിശാസ്ത്രം",

    "about_title": "സാങ്കേതിക ഘടനയും രോഗശാസ്ത്രവും",

    "about_desc": "ResNet-50 മോഡൽ, Grad-CAM layer4 വിശദീകരണ AI, 4-വിഭാഗ രോഗവർഗ്ഗീകരണം എന്നിവയുടെ സമഗ്ര വിവരണം.",

    "about_launch_btn": "പരിശോധന ആരംഭിക്കുക",

    "about_guide_btn": "ഫീൽഡ് ഗൈഡ് കാണുക ↗",

    "about_card1_title": "ന്യൂറൽ നെറ്റ്‌വർക്ക് ഘടന",

    "about_card1_sub": "ഡീപ് ഫീച്ചറുകളോടെയുള്ള ട്രാൻസ്ഫർ ലേണിംഗ്",

    "about_card1_p1": "അടക്കയുടെ ഓലകളിലെയും കായ്കളിലെയും രോഗങ്ങൾ കൃത്യമായി തിരിച്ചറിയാൻ ResNet-50 മോഡൽ ഉപയോഗിക്കുന്നു.",

    "about_backbone_label": "ബാക്ക്ബോൺ:",

    "about_backbone_desc": "50 കൺവല്യൂഷണൽ ലെയറുകൾ",

    "about_head_label": "ക്ലാസിഫിക്കേഷൻ ഹെഡ്:",

    "about_head_desc": "4 വിഭാഗങ്ങൾക്കായുള്ള ലീനിയർ ലെയർ (2048 → 4 ക്ലാസ്സുകൾ)",

    "about_tensor_label": "ഇൻപുട്ട് ടെൻസർ:",

    "about_tensor_desc": "224 × 224 × 3 (RGB ഇമേജ്)",

    "about_xai_label": "വിശദീകരണം (XAI):",

    "about_xai_desc": "layer4 അടിസ്ഥാനമാക്കിയുള്ള Grad-CAM ഹീറ്റ്മാപ്പ്",

    "about_infer_label": "വേഗത:",

    "about_infer_desc": "100 മില്ലിസെക്കൻഡിൽ താഴെ വേഗതയിൽ പരിശോധനാ ഫലം",

    "about_card2_title": "വിശദീകരണ AI (Grad-CAM)",

    "about_card2_sub": "ഗ്രേഡിയന്റ് അധിഷ്ഠിത ഹീറ്റ്മാപ്പ്",

    "about_card2_p1": "കർഷകർക്ക് വ്യക്തത നൽകാൻ, മോഡൽ എവിടെയാണ് ശ്രദ്ധ കേന്ദ്രീകരിച്ചതെന്ന് ഹീറ്റ്മാപ്പ് വഴി കാണിക്കുന്നു:",

    "about_card2_p2": "രോഗലക്ഷണങ്ങളെ കൃത്യമായി വേർതിരിച്ച് ചിത്രത്തിന് മുകളിൽ താപ മാപ്പായി പ്രദർശിപ്പിക്കുന്നു.",

    "about_tax_title": "4-വിഭാഗ രോഗവർഗ്ഗീകരണം",

    "about_tax_sub": "സവിശേഷതകൾ, കാരണങ്ങൾ, പ്രതിരോധ മാർഗ്ഗങ്ങൾ",

    "status_healthy": "ആരോഗ്യമുള്ളത്",

    "status_diseased": "രോഗബാധിതം",

    "recom_action_label": "ശുപാർശ ചെയ്ത പ്രതിരോധം:",

    "desc_healthy_nut": "കുമിൾ പാടുകളില്ലാത്ത, നല്ല ഘടനയും ഭാരവുമുള്ള ആരോഗ്യമുള്ള അടക്ക.",

    "mgmt_healthy_nut": "നനയും സന്തുലിത വളപ്രയോഗവും (NPK) കൃത്യമായി നൽകുക.",

    "desc_healthy_leaf": "മഞ്ഞളിപ്പില്ലാത്ത തിളക്കമുള്ള പച്ച നിറത്തിലുള്ള ആരോഗ്യമുള്ള ഓല.",

    "mgmt_healthy_leaf": "മഴക്കാലത്ത് വേരുകളിൽ വെള്ളം കെട്ടിനിൽക്കാതെ നോക്കുക.",

    "desc_mahali": "ഫൈറ്റോപ്ത്തോറ കുമിൾ മൂലമുണ്ടാകുന്ന മഹാളി രോഗം; അടക്ക കൊഴിച്ചിലിന് കാരണമാകുന്നു.",

    "mgmt_mahali": "കാലവർഷത്തിന് മുൻപ് 1% ബോർഡോ മിശ്രിതം തളിക്കുക; പോളിത്തീൻ ഷീറ്റ് കെട്ടുക.",

    "desc_yellow_leaf_disease": "ഫൈറ്റോപ്ലാസ്മ മൂലമുണ്ടാകുന്ന മഞ്ഞളിപ്പ് രോഗം; ഓലകൾ മഞ്ഞളിക്കുകയും വിളവ് കുറയുകയും ചെയ്യുന്നു.",

    "mgmt_yellow_leaf_disease": "സന്തുലിത വളത്തോടൊപ്പം മഗ്നീഷ്യവും ജൈവവളവും നൽകുക."

  }

};



  const CLASS_NAMES_I18N = {

    mahali: {

      en: 'Mahali / Koleroga (Fruit Rot)',

      kn: 'ಮಹಾಲಿ / ಕೊಳೆರೋಗ (ಹಣ್ಣು ಕೊಳೆ)',

      hi: 'महाली / कोलेरोगा (फल सड़न)',

      ml: 'മഹാലി / കൊളെറോഗ (കായ്ചീയൽ)'

    },

    yld: {

      en: 'Yellow Leaf Disease (YLD)',

      kn: 'ಹಳದಿ ಎಲೆ ರೋಗ (ವೈಎಲ್‌ಡಿ)',

      hi: 'पीला पत्ता रोग (वाईएलडी)',

      ml: 'മഞ്ഞളിപ്പ് രോഗം (വൈഎൽഡി)'

    },

    healthy_nut: {

      en: 'Healthy Nut',

      kn: 'ಆರೋಗ್ಯಕರ ಅಡಿಕೆ',

      hi: 'स्वस्थ सुपारी',

      ml: 'ആരോഗ്യമുള്ള അടക്ക'

    },

    healthy_leaf: {

      en: 'Healthy Leaf',

      kn: 'ಆರೋಗ್ಯಕರ ಎಲೆ',

      hi: 'स्वस्थ पत्ता',

      ml: 'ആരോഗ്യമുള്ള ഇല'

    }

  };



  function translateDiseaseName(name, lang) {

    if (!name) return name;

    const lower = name.toLowerCase();

    let key = null;

    if (lower.includes('mahali') || lower.includes('koleroga') || lower.includes('rot') || lower.includes('ಕೊಳೆ') || lower.includes('सड़न') || lower.includes('ചീയൽ')) key = 'mahali';

    else if (lower.includes('yellow') || lower.includes('yld') || lower.includes('ಹಳದಿ') || lower.includes('पीला') || lower.includes('മഞ്ഞളിപ്പ്')) key = 'yld';

    else if (lower.includes('nut') || lower.includes('ಅಡಿಕೆ') || lower.includes('सुपारी') || lower.includes('അടക്ക')) key = 'healthy_nut';

    else if (lower.includes('leaf') || lower.includes('ಎಲೆ') || lower.includes('पत्ता') || lower.includes('ഇല')) key = 'healthy_leaf';



    if (key && CLASS_NAMES_I18N[key] && CLASS_NAMES_I18N[key][lang]) {

      return CLASS_NAMES_I18N[key][lang];

    }

    return name;

  }



  function getDiseaseKeyFromName(name) {

    if (!name) return 'healthy_nut';

    const lower = name.toLowerCase();

    if (lower.includes('mahali') || lower.includes('koleroga') || lower.includes('rot') || lower.includes('ಕೊಳೆ') || lower.includes('सड़न') || lower.includes('ചീയൽ')) return 'mahali';

    if (lower.includes('yellow') || lower.includes('yld') || lower.includes('ಹಳದಿ') || lower.includes('पीला') || lower.includes('മഞ്ഞളിപ്പ്')) return 'yld';

    if (lower.includes('leaf') || lower.includes('ಎಲೆ') || lower.includes('पत्ता') || lower.includes('ഇല')) return 'healthy_leaf';

    return 'healthy_nut';

  }



  const UNDERSTANDING_BULLETS_I18N = {

    en: {

      mahali: [

        'The model strongly favors this class: <strong>Mahali / Koleroga (Fruit Rot)</strong>. This does not confirm a diagnosis.',

        'Fruiting bunches show dark, water-soaked lesions and premature shedding of green buttons and nuts.',

        '<strong>Recommended care:</strong> Spray 1% Bordeaux mixture before monsoon and tie polythene covers (125-gauge) over bunches.',

        'Take another photo in daylight, hold the camera steady and fill the frame with the leaf or nut.',

        'If you are worried, show the palm to an agricultural officer or a KVK.',

        'The heatmap shows where the model looked. It does not prove the cause of the problem. Only an expert can confirm a disease.'

      ],

      yld: [

        'The model strongly favors this class: <strong>Yellow Leaf Disease (YLD)</strong>. This does not confirm a diagnosis.',

        'Debilitating systemic condition with characteristic chlorosis and yellowing starting from leaflet tips.',

        '<strong>Recommended care:</strong> Improve soil drainage, apply balanced NPK (100:40:140g) plus 12 kg organic manure per palm annually.',

        'Take another photo in daylight, hold the camera steady and fill the frame with the leaf or nut.',

        'If you are worried, show the palm to an agricultural officer or a KVK.',

        'The heatmap shows where the model looked. It does not prove the cause of the problem. Only an expert can confirm a disease.'

      ],

      healthy_nut: [

        'The model strongly favors this class: <strong>Healthy Nut</strong>. This does not confirm a diagnosis.',

        'Nut cluster exhibits robust physical attachment, pristine pericarp, and absence of necrotic rot or fungal mycelium.',

        '<strong>Recommended care:</strong> Maintain scientific seasonal irrigation (175–200 L/palm every 4–6 days) and micronutrients (Borax 12g + Zinc 20g).',

        'Take another photo in daylight, hold the camera steady and fill the frame with the leaf or nut.',

        'If you are worried, show the palm to an agricultural officer or a KVK.',

        'The heatmap shows where the model looked. It does not prove the cause of the problem.'

      ],

      healthy_leaf: [

        'The model strongly favors this class: <strong>Healthy Leaf</strong>. This does not confirm a diagnosis.',

        'Foliage exhibits vigorous deep green chlorophyll coloration, balanced pinnate architecture, and erect central growing spindle.',

        '<strong>Recommended care:</strong> Maintain 9 to 12 functional green fronds per palm, pre-monsoon crown cleaning, and balanced split fertilizer.',

        'Take another photo in daylight, hold the camera steady and fill the frame with the leaf or nut.',

        'If you are worried, show the palm to an agricultural officer or a KVK.',

        'The heatmap shows where the model looked. It does not prove the cause of the problem.'

      ]

    },

    kn: {

      mahali: [

        'ಮಾದರಿಯು ಈ ವರ್ಗವನ್ನು ಹೆಚ್ಚು ಬೆಂಬಲಿಸುತ್ತದೆ: <strong>ಮಹಾಲಿ / ಕೊಳೆರೋಗ (ಹಣ್ಣು ಕೊಳೆ)</strong>. ಇದು ಅಂತಿಮ ರೋಗನಿರ್ಣಯವಲ್ಲ.',

        'ಗೊನೆಗಳಲ್ಲಿ ಕಪ್ಪು ಬಣ್ಣದ ನೀರಿನ ಕಲೆಗಳು ಮತ್ತು ಎಳೆಯ ಹಸಿರು ಅಡಿಕೆಗಳ ಅಕಾಲಿಕ ಉದುರುವಿಕೆ ಕಂಡುಬರುತ್ತದೆ.',

        '<strong>ಶಿಫಾರಸು ಮಾಡಿದ ಆರೈಕೆ:</strong> ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ ೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ ಮತ್ತು ೧೨೫-ಗೇಜ್ ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ ಕಟ್ಟಿ.',

        'ಹಗಲಿನ ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಮತ್ತೊಂದು ಫೋಟೋ ತೆಗೆಯಿರಿ, ಕ್ಯಾಮೆರಾವನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದುಕೊಳ್ಳಿ.',

        'ಆತಂಕವಿದ್ದರೆ, ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರಕ್ಕೆ (KVK) ಗಿಡವನ್ನು ತೋರಿಸಿ.',

        'ಹೀಟ್‌ಮ್ಯಾಪ್ ಮಾದರಿಯು ಗಮನಿಸಿದ ಭಾಗವನ್ನು ತೋರಿಸುತ್ತದೆ. ಕೃಷಿ ತಜ್ಞರ ದೃಢೀಕರಣ ಮುಖ್ಯ.'

      ],

      yld: [

        'ಮಾದರಿಯು ಈ ವರ್ಗವನ್ನು ಹೆಚ್ಚು ಬೆಂಬಲಿಸುತ್ತದೆ: <strong>ಹಳದಿ ಎಲೆ ರೋಗ (ವೈಎಲ್‌ಡಿ)</strong>. ಇದು ಅಂತಿಮ ರೋಗನಿರ್ಣಯವಲ್ಲ.',

        'ಎಲೆಗಳ ತುದಿಯಿಂದ ಪ್ರಾರಂಭವಾಗುವ ವಿಶಿಷ್ಟ ಹಳದಿ ಬಣ್ಣ ಮತ್ತು ಗರಿಗಳ ಕ್ಷೀಣತೆ ಕಂಡುಬರುತ್ತದೆ.',

        '<strong>ಶಿಫಾರಸು ಮಾಡಿದ ಆರೈಕೆ:</strong> ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ನಿರ್ಮಿಸಿ, ಸಮತೋಲಿತ NPK (೧೦೦:೪೦:೧೪೦ ಗ್ರಾಂ) ಮತ್ತು ೧೨ ಕೆಜಿ ಕಾಂಪೋಸ್ಟ್ ಗೊಬ್ಬರ ನೀಡಿ.',

        'ಹಗಲಿನ ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಮತ್ತೊಂದು ಫೋಟೋ ತೆಗೆಯಿರಿ, ಕ್ಯಾಮೆರಾವನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದುಕೊಳ್ಳಿ.',

        'ಆತಂಕವಿದ್ದರೆ, ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರಕ್ಕೆ (KVK) ಗಿಡವನ್ನು ತೋರಿಸಿ.',

        'ಹೀಟ್‌ಮ್ಯಾಪ್ ಮಾದರಿಯು ಗಮನಿಸಿದ ಭಾಗವನ್ನು ತೋರಿಸುತ್ತದೆ. ಕೃಷಿ ತಜ್ಞರ ದೃಢೀಕರಣ ಮುಖ್ಯ.'

      ],

      healthy_nut: [

        'ಮಾದರಿಯು ಈ ವರ್ಗವನ್ನು ಹೆಚ್ಚು ಬೆಂಬಲಿಸುತ್ತದೆ: <strong>ಆರೋಗ್ಯಕರ ಅಡಿಕೆ</strong>. ಇದು ಅಂತಿಮ ರೋಗನಿರ್ಣಯವಲ್ಲ.',

        'ಅಡಿಕೆ ಗೊನೆಯು ಗಟ್ಟಿಯಾದ ತೊಟ್ಟಿನ ಹಿಡಿತ, ನಯವಾದ ಸಿಪ್ಪೆ ಮತ್ತು ಯಾವುದೇ ಶಿಲೀಂಧ್ರ ಕಲೆಗಳಿಲ್ಲದೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ.',

        '<strong>ಶಿಫಾರಸು ಮಾಡಿದ ಆರೈಕೆ:</strong> ಬೇಸಿಗೆಯಲ್ಲಿ ನಿಯಮಿತ ನೀರಾವರಿ (೧೭೫–೨೦೦ ಲೀಟರ್ ಪ್ರತಿ ಮರಕ್ಕೆ) ಮತ್ತು ಲಘು ಪೋಷಕಾಂಶ (ಬೋರಾಕ್ಸ್ ೧೨ ಗ್ರಾಂ + ಸತು ೨೦ ಗ್ರಾಂ) ನೀಡಿ.',

        'ಹಗಲಿನ ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಮತ್ತೊಂದು ಫೋಟೋ ತೆಗೆಯಿರಿ, ಕ್ಯಾಮೆರಾವನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದುಕೊಳ್ಳಿ.',

        'ಯಾವುದೇ ಸಂಶಯವಿದ್ದರೆ ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.',

        'ಹೀಟ್‌ಮ್ಯಾಪ್ ಮಾದರಿಯು ಗಮನಿಸಿದ ಭಾಗವನ್ನು ತೋರಿಸುತ್ತದೆ.'

      ],

      healthy_leaf: [

        'ಮಾದರಿಯು ಈ ವರ್ಗವನ್ನು ಹೆಚ್ಚು ಬೆಂಬಲಿಸುತ್ತದೆ: <strong>ಆರೋಗ್ಯಕರ ಎಲೆ</strong>. ಇದು ಅಂತಿಮ ರೋಗನಿರ್ಣಯವಲ್ಲ.',

        'ಗರಿಗಳು ದಟ್ಟ ಹಸಿರು ಬಣ್ಣ, ಸಮತೋಲಿತ ರಚನೆ ಮತ್ತು ನೇರವಾದ ಆರೋಗ್ಯಕರ ಸುಳಿಯನ್ನು ಹೊಂದಿವೆ.',

        '<strong>ಶಿಫಾರಸು ಮಾಡಿದ ಆರೈಕೆ:</strong> ಮರದಲ್ಲಿ ೯ ರಿಂದ ೧೨ ಹಸಿರು ಗರಿಗಳನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ, ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ ಕಿರೀಟ ಸ್ವಚ್ಛತೆ ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರ ನೀಡಿ.',

        'ಹಗಲಿನ ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಮತ್ತೊಂದು ಫೋಟೋ ತೆಗೆಯಿರಿ, ಕ್ಯಾಮೆರಾವನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದುಕೊಳ್ಳಿ.',

        'ಯಾವುದೇ ಸಂಶಯವಿದ್ದರೆ ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.',

        'ಹೀಟ್‌ಮ್ಯಾಪ್ ಮಾದರಿಯು ಗಮನಿಸಿದ ಭಾಗವನ್ನು ತೋರಿಸುತ್ತದೆ.'

      ]

    },

    hi: {

      mahali: [

        'मॉडल इस वर्ग का दृढ़ता से समर्थन करता है: <strong>महाली / कोलेरोगा (फल सड़न)</strong>। यह अंतिम निदान नहीं है।',

        'फलों के गुच्छों पर गहरे जल-सिक्त धब्बे और कच्चे फलों का गिरना देखा जाता है।',

        '<strong>अनुशंसित देखभाल:</strong> मानसून से पहले 1% बोर्डो मिश्रण का छिड़काव करें और गुच्छों को 125-गेज पॉलीथीन से ढकें।',

        'दिन के उजाले में दूसरी फोटो लें, कैमरे को स्थिर रखें।',

        'यदि संशय हो, तो कृषि अधिकारी या कृषि विज्ञान केंद्र (KVK) से संपर्क करें।',

        'हीटमैप दिखाता है कि मॉडल ने कहाँ देखा। विशेषज्ञ द्वारा पुष्टि आवश्यक है।'

      ],

      yld: [

        'मॉडल इस वर्ग का दृढ़ता से समर्थन करता है: <strong>पीला पत्ता रोग (वाईएलडी)</strong>। यह अंतिम निदान नहीं है।',

        'पत्तियों के सिरों से शुरू होकर पीलापन और वृक्ष के मुकुट का संकुचित होना देखा जाता है।',

        '<strong>अनुशंसित देखभाल:</strong> जल निकासी सुधारें, प्रति वृक्ष संतुलित NPK (100:40:140 ग्राम) और 12 किग्रा जैविक खाद दें।',

        'दिन के उजाले में दूसरी फोटो लें, कैमरे को स्थिर रखें।',

        'यदि संशय हो, तो कृषि अधिकारी या कृषि विज्ञान केंद्र (KVK) से संपर्क करें।',

        'हीटमैप दिखाता है कि मॉडल ने कहाँ देखा। विशेषज्ञ द्वारा पुष्टि आवश्यक है।'

      ],

      healthy_nut: [

        'मॉडल इस वर्ग का दृढ़ता से समर्थन करता है: <strong>स्वस्थ सुपारी</strong>। यह अंतिम निदान नहीं है।',

        'सुपारी का गुच्छा मजबूत लगाव, स्वच्छ छिलका और बिना किसी कवक सड़न के स्वस्थ है।',

        '<strong>अनुशंसित देखभाल:</strong> वैज्ञानिक सिंचाई (175-200 लीटर प्रति वृक्ष) और सूक्ष्म पोषक तत्व (बोरेक्स 12 ग्राम + जिंक 20 ग्राम) बनाए रखें।',

        'दिन के उजाले में दूसरी फोटो लें, कैमरे को स्थिर रखें।',

        'विशेषज्ञ मार्गदर्शन के लिए स्थानीय कृषि अधिकारी से संपर्क करें।',

        'हीटमैप दिखाता है कि मॉडल ने कहाँ देखा।'

      ],

      healthy_leaf: [

        'मॉडल इस वर्ग का दृढ़ता से समर्थन करता है: <strong>स्वस्थ पत्ता</strong>। यह अंतिम निदान नहीं है।',

        'पत्तियाँ गहरा हरा रंग, संतुलित विन्यास और सीधी स्वस्थ केंद्रीय कोपल प्रदर्शित करती हैं।',

        '<strong>अनुशंसित देखभाल:</strong> प्रति वृक्ष 9 से 12 हरी पत्तियाँ बनाए रखें, मानसून पूर्व मुकुट सफाई और संतुलित उर्वरक दें।',

        'दिन के उजाले में दूसरी फोटो लें, कैमरे को स्थिर रखें।',

        'विशेषज्ञ मार्गदर्शन के लिए स्थानीय कृषि अधिकारी से संपर्क करें।',

        'हीटमैप दिखाता है कि मॉडल ने कहाँ देखा।'

      ]

    },

    ml: {

      mahali: [

        'മോഡൽ ഈ വിഭാഗത്തെ കൂടുതൽ സൂചിപ്പിക്കുന്നു: <strong>മഹാലി / കൊളെറോഗ (കായ്ചീയൽ)</strong>. ഇത് അന്തിമ രോഗനിർണ്ണയമല്ല.',

        'കുലകളിൽ ഇരുണ്ട പാടുകളും ഇളം അടക്കകൾ കൊഴിഞ്ഞു വീഴുന്നതും കാണാം.',

        '<strong>ശുപാർശ ചെയ്യുന്ന പരിചരണം:</strong> മഴയ്ക്ക് മുൻപ് 1% ബോർഡോ മിശ്രിതം തളിക്കുക, 125-ഗേജ് പോളിത്തീൻ കൊണ്ട് കുലകൾ മൂടുക.',

        'പകൽ വെളിച്ചത്തിൽ മറ്റൊരു ഫോട്ടോ എടുക്കുക, ക്യാമറ അനങ്ങാതെ പിടിക്കുക.',

        'സംശയമുണ്ടെങ്കിൽ അടുത്തുള്ള കൃഷി ഭവനിലോ കൃഷി വിജ്ഞാന കേന്ദ്രത്തിലോ ബന്ധപ്പെടുക.',

        'ഹീറ്റ്മാപ്പ് മോഡൽ ശ്രദ്ധിച്ച ഭാഗങ്ങളെ കാണിക്കുന്നു. വിദഗ്ദ്ധ പരിശോധന ആവശ്യമാണ്.'

      ],

      yld: [

        'മോഡൽ ഈ വിഭാഗത്തെ കൂടുതൽ സൂചിപ്പിക്കുന്നു: <strong>മഞ്ഞളിപ്പ് രോഗം (വൈഎൽഡി)</strong>. ഇത് അന്തിമ രോഗനിർണ്ണയമല്ല.',

        'ഓലകളുടെ അറ്റത്ത് നിന്ന് തുടങ്ങുന്ന കടുത്ത മഞ്ഞനിറവും മണ്ട ചെറുതാകലും കാണപ്പെടുന്നു.',

        '<strong>ശുപാർശ ചെയ്യുന്ന പരിചരണം:</strong> നീർവാർച്ച ഉറപ്പാക്കുക, ഒരു തെങ്ങിന് സന്തുലിത എൻപികെ (100:40:140 ഗ്രാം), 12 കിലോ ജൈവവളം നൽകുക.',

        'പകൽ വെളിച്ചത്തിൽ മറ്റൊരു ഫോട്ടോ എടുക്കുക, ക്യാമറ അനങ്ങാതെ പിടിക്കുക.',

        'സംശയമുണ്ടെങ്കിൽ അടുത്തുള്ള കൃഷി ഭവനിലോ കൃഷി വിജ്ഞാന കേന്ദ്രത്തിലോ ബന്ധപ്പെടുക.',

        'ഹീറ്റ്മാപ്പ് മോഡൽ ശ്രദ്ധിച്ച ഭാഗങ്ങളെ കാണിക്കുന്നു. വിദഗ്ദ്ധ പരിശോധന ആവശ്യമാണ്.'

      ],

      healthy_nut: [

        'മോഡൽ ഈ വിഭാഗത്തെ കൂടുതൽ സൂചിപ്പിക്കുന്നു: <strong>ആരോഗ്യമുള്ള അടക്ക</strong>. ഇത് അന്തിമ രോഗനിർണ്ണയമല്ല.',

        'അടക്കക്കുല നല്ല ബലമുള്ളതും മിനുസമുള്ള തൊലിയോടും കൂടിയതുമാണ്.',

        '<strong>ശുപാർശ ചെയ്യുന്ന പരിചരണം:</strong> വേനൽക്കാലത്ത് ആവശ്യത്തിന് നനയ്ക്കലും (175-200 ലിറ്റർ), സൂക്ഷ്മമൂലകങ്ങളും (ബോറാക്സ് 12 ഗ്രാം + സിങ്ക് 20 ഗ്രാം) നൽകുക.',

        'പകൽ വെളിച്ചത്തിൽ മറ്റൊരു ഫോട്ടോ എടുക്കുക, ക്യാമറ അനങ്ങാതെ പിടിക്കുക.',

        'സംശയമുണ്ടെങ്കിൽ കൃഷി വിദഗ്ദ്ധരുമായി ബന്ധപ്പെടുക.',

        'ഹീറ്റ്മാപ്പ് മോഡൽ ശ്രദ്ധിച്ച ഭാഗങ്ങളെ കാണിക്കുന്നു.'

      ],

      healthy_leaf: [

        'മോഡൽ ഈ വിഭാഗത്തെ കൂടുതൽ സൂചിപ്പിക്കുന്നു: <strong>ആരോഗ്യമുള്ള ഇല</strong>. ഇത് അന്തിമ രോഗനിർണ്ണയമല്ല.',

        'ഓലകൾ തിളക്കമുള്ള പച്ചപ്പും ആരോഗ്യമുള്ള കുരുത്തോലയും കാണിക്കുന്നു.',

        '<strong>ശുപാർശ ചെയ്യുന്ന പരിചരണം:</strong> തെങ്ങിൽ 9 മുതൽ 12 വരെ പച്ച ഓലകൾ നിലനിർത്തുക, മഴയ്ക്ക് മുൻപ് മണ്ട വൃത്തിയാക്കലും വളപ്രയോഗവും നടത്തുക.',

        'പകൽ വെളിച്ചത്തിൽ മറ്റൊരു ഫോട്ടോ എടുക്കുക, ക്യാമറ അനങ്ങാതെ പിടിക്കുക.',

        'സംശയമുണ്ടെങ്കിൽ കൃഷി വിദഗ്ദ്ധരുമായി ബന്ധപ്പെടുക.',

        'ഹീറ്റ്മാപ്പ് മോഡൽ ശ്രദ്ധിച്ച ഭാഗങ്ങളെ കാണിക്കുന്നു.'

      ]

    }

  };



  const DOSSIER_I18N = {

    en: {

      mahali: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>1. What Causes It (Etiology & Epidemiology)</span></h3>

            <p class="dossier-block-text">Mahali (also universally recognized as Koleroga) is caused by the destructive oomycete pathogen <strong><em>Phytophthora meadii</em> McRae</strong>.</p>

            <ul class="dossier-bullets">

              <li><strong>Climatic Triggers:</strong> High relative humidity (>90%), continuous drizzling rain, overcast skies, low sunlight, and temperatures hovering between 20°C and 24°C during the Southwest monsoon season (June to September).</li>

              <li><strong>Mode of Spread:</strong> Rain splashes readily detach and disperse asexual sporangia and motile biflagellate zoospores across neighboring bunches and adjacent palms.</li>

              <li><strong>Survival Mechanism:</strong> The pathogen overwinters as resilient resting oospores in dried mummified nut bunches, tree crown crevices, and rotting nuts on the plantation floor.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>2. How It Affects the Palm (Pathological Progression & Yield Loss)</span></h3>

            <p class="dossier-block-text">Infection initiates rapid necrotic decay of the reproductive bunch and can advance systemically into the palm crown:</p>

            <ul class="dossier-bullets">

              <li><strong>Initial Symptoms:</strong> Water-soaked, dark green, translucent lesions emerge near the perianth (calyx end) of young tender nuts.</li>

              <li><strong>Advanced Fruit Rot:</strong> Infected nuts rapidly darken, lose their turgidity, rot, and shed in immense numbers (premature button and nut shedding). Fallen nuts develop a conspicuous dense white cottony fungal mycelial felt.</li>

              <li><strong>Crown Rot & Bud Rot:</strong> If rain washes pathogen propagules into the terminal bud/crown, the central growing spindle wilts, turns necrotic brown, collapses, and completely destroys the palm crown.</li>

              <li><strong>Economic Loss:</strong> In unmanaged gardens, fruit rot destroys between <strong>50% and 90%</strong> of the seasonal crop harvest.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. How to Overcome (ICAR-CPCRI Management Protocols)</span></h3>

            <p class="dossier-block-text">Integrated phytosanitary management certified by ICAR-CPCRI combines chemical prophylaxis, physical barriers, and cultural sanitation:</p>

            <ul class="dossier-bullets">

              <li><strong>Prophylactic Bordeaux Mixture (1%):</strong> Prepare by dissolving 1 kg copper sulfate and 1 kg slaked lime in 100 liters of water. Spray finely over all bunches:<br>• <em>1st Spray:</em> Immediately before the onset of monsoon showers (May-June).<br>• <em>2nd Spray:</em> 40 to 45 days later during a monsoon break (July-August).<br>• <em>3rd Spray:</em> If rains continue late into September.</li>

              <li><strong>Polythene Bunch Covering:</strong> Tie 125-gauge polythene covers (75 × 60 cm) over the entire bunch prior to the onset of monsoon showers. Bunch covering provides complete mechanical defense against rain-borne fungal zoospores.</li>

              <li><strong>Field Hygiene & Sanitation:</strong> Collect and incinerate all fallen, rotten nuts and diseased rachis debris; never leave them to decompose in the plantation.</li>

              <li><strong>Soil Drainage:</strong> Excavate 2-3 feet deep drainage ditches between rows to prevent water saturation around palm root zones.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>4. Comparative Trade-offs (Advantages vs. Disadvantages)</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>Management Strategy</th><th>Key Advantages (Benefits)</th><th>Key Disadvantages (Limitations)</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">1% Bordeaux Mixture Spray</td>

                    <td><span class="tag-adv">✓ High Efficacy:</span> Broad-spectrum fungicidal barrier.<br><span class="tag-adv">✓ Cost-Effective:</span> Standard proven ICAR recommendation.<br><span class="tag-adv">✓ Canopy Coverage:</span> Protects entire surface area of bunches.</td>

                    <td><span class="tag-dis">✗ Rain Wash-off:</span> Torrential downpours immediately after spraying can wash away deposits.<br><span class="tag-dis">✗ Labor Heavy:</span> Requires skilled tree climbers or power rocker sprayers.<br><span class="tag-dis">✗ Timing Sensitive:</span> Ineffective if applied late after systemic rot begins.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Polythene Bunch Covering</td>

                    <td><span class="tag-adv">✓ 100% Chemical-Free:</span> Zero chemical residue on nuts.<br><span class="tag-adv">✓ Rainproof Barrier:</span> Stops all rain splash spore transmission.<br><span class="tag-adv">✓ Single Application:</span> Done once before monsoon season.</td>

                    <td><span class="tag-dis">✗ Initial Labor:</span> Requires climbing every palm to securely tie covers.<br><span class="tag-dis">✗ Condensation Risk:</span> Improper tying can trap internal humidity.<br><span class="tag-dis">✗ Post-Season Removal:</span> Covers must be removed after rains.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Cultural Phytosanitation</td>

                    <td><span class="tag-adv">✓ Inoculum Reduction:</span> Breaks the overwintering fungal lifecycle.<br><span class="tag-adv">✓ Zero Material Cost:</span> Requires only routine orchard collection.<br><span class="tag-adv">✓ Permanent Benefit:</span> Lowers plantation pathogen pressure year-round.</td>

                    <td><span class="tag-dis">✗ Community Dependent:</span> Ineffective if adjacent neglected orchards harbor active disease.<br><span class="tag-dis">✗ Non-Curative:</span> Does not prevent airborne spores from settling on palms during storms.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>5. Research Authority & Extension Support</span></h3>

            <p class="dossier-block-text">Technical guidance adapted from <strong>ICAR-Central Plantation Crops Research Institute (CPCRI)</strong>, Kasaragod, Kerala & Regional Station Vittal, Karnataka.<br><em>Official Helpline:</em> Contact your local Krishi Vigyan Kendra (KVK) or Assistant Director of Horticulture for chemical dosage verification.</p>

          </div>

        </div>

      `,

      yld: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>1. What Causes It (Etiology & Vectors)</span></h3>

            <p class="dossier-block-text">Yellow Leaf Disease (YLD) is a debilitating systemic disorder associated with <strong>Phytoplasma</strong> organisms that inhabit the phloem tissue of the palm.</p>

            <ul class="dossier-bullets">

              <li><strong>Insect Vectors:</strong> Transmitted by phloem-feeding plant hoppers (<em>Proutista moesta</em>) and lace bugs (<em>Stephanitis typica</em>).</li>

              <li><strong>Predisposing Factors:</strong> Waterlogging, high soil acidity (low pH), severe root hypoxia, and inadequate soil potassium/magnesium levels accelerate symptom onset.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>2. How It Affects the Palm (Pathological Progression & Yield Loss)</span></h3>

            <p class="dossier-block-text">YLD causes slow, relentless systemic degeneration over several harvest cycles:</p>

            <ul class="dossier-bullets">

              <li><strong>Foliar Chlorosis:</strong> Intense yellowing initiates at the tips of outer leaflets in lower whorls, progressing along lamina edges leaving green vascular bands.</li>

              <li><strong>Crown Reduction:</strong> Fronds become brittle, shorten in length, and the entire crown shrinks, giving the palm a tapered appearance.</li>

              <li><strong>Kernel Deterioration:</strong> Nuts become small, cracked, blackened with unmarketable spongy, blackened endosperm (soft, degraded chali).</li>

              <li><strong>Yield Impact:</strong> Over 3-5 years, yield drops by <strong>60% to 80%</strong>, causing severe financial hardship for growers.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. How to Overcome (ICAR-CPCRI Management Protocols)</span></h3>

            <p class="dossier-block-text">Because phytoplasma is systemic within vascular tissue, there is no chemical cure. Management focuses on soil rehabilitation and immunity enhancement:</p>

            <ul class="dossier-bullets">

              <li><strong>Balanced Nutrition (NPK):</strong> Apply 100 g Nitrogen (220 g Urea), 40 g Phosphorus (200 g Rock Phosphate), and 140 g Potassium (230 g Muriate of Potash) per palm per year in two splits (May-June and Sept-Oct).</li>

              <li><strong>Organic Enrichment:</strong> Apply 12 kg organic compost/farmyard manure and 12 kg green leaf mulch per palm annually.</li>

              <li><strong>Drainage Rectification:</strong> Construct deep drainage channels to prevent stagnant water during the monsoon.</li>

              <li><strong>Intercropping:</strong> Grow cocoa, banana, and cover crops (<em>Mimosa invisa</em>) to improve soil biological activity.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>4. Comparative Trade-offs (Advantages vs. Disadvantages)</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>Management Approach</th><th>Key Advantages (Benefits)</th><th>Key Disadvantages (Limitations)</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">Nutritional Rejuvenation (NPK + Compost)</td>

                    <td><span class="tag-adv">✓ Palm Longevity:</span> Rebuilds canopy vigor and kernel weight.<br><span class="tag-adv">✓ Sustainable:</span> Enhances beneficial soil microbiome.</td>

                    <td><span class="tag-dis">✗ No Cure:</span> Does not eradicate phytoplasma from phloem.<br><span class="tag-dis">✗ Multi-Year Effort:</span> Visible recovery requires 2-3 seasons.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Drainage Improvement</td>

                    <td><span class="tag-adv">✓ Root Health:</span> Prevents root asphyxiation and secondary rot.<br><span class="tag-adv">✓ Moisture Balance:</span> Prevents seasonal waterlogging shock.</td>

                    <td><span class="tag-dis">✗ Earthwork Cost:</span> Trenching in hilly terrain requires capital investment.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Roguing Severely Declining Palms</td>

                    <td><span class="tag-adv">✓ Vector Control:</span> Removes primary inoculum sources in orchard.<br><span class="tag-adv">✓ Resource Allocation:</span> Lets farmer focus inputs on viable trees.</td>

                    <td><span class="tag-dis">✗ Direct Loss:</span> Eradicates mature trees with immediate loss of stand.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>5. Research Authority & Extension Support</span></h3>

            <p class="dossier-block-text">Refer to <strong>ICAR-CPCRI Technical Bulletin: Yellow Leaf Disease of Arecanut</strong>. Consult your district horticulture officer for soil testing and micronutrient analysis.</p>

          </div>

        </div>

      `,

      healthy_nut: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🌰</span><span>1. Botanical & Morphological Quality Benchmarks</span></h3>

            <p class="dossier-block-text">Healthy arecanut (<em>Areca catechu</em>) clusters represent the gold-standard phytosanitary baseline: robust mechanical attachment, pristine pericarps, and uncompromised internal ruminate endosperms.</p>

            <ul class="dossier-bullets">

              <li><strong>Epicarp & Pericarp Integrity:</strong> Smooth, lustrous, unbroken epidermal surface with vibrant coloration ranging from glossy deep emerald green to radiant golden-saffron orange. Free of water-soaked depressions or fungal mats.</li>

              <li><strong>Calyx & Pedicel Anchorage:</strong> Tight mechanical clasp at the perianth socket. Resists premature monsoon shedding, requiring >18 N of tensile detachment force.</li>

              <li><strong>Ruminate Endosperm Architecture:</strong> Dense, solid kernel interior featuring the signature marble-veined ruminate albumen with high specific gravity and rich polyphenols (arecoline, arecaidine).</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>📈</span><span>2. Phenological Development & Nut Maturation Stages</span></h3>

            <p class="dossier-block-text">Understanding the 9-month development cycle is essential for timely disease prevention and harvesting:</p>

            <ul class="dossier-bullets">

              <li><strong>Button / Pre-Nut Stage (Batte Adike — Months 1–2):</strong> Delicate post-pollination ovary set. Highly susceptible to moisture shock and boron deficiency button drop.</li>

              <li><strong>Tender Green Nut Stage (Chali / Tender — Months 3–5):</strong> Rapid enlargement phase with active endosperm synthesis. Peak vulnerability window for <em>Phytophthora meadii</em> (Mahali/Koleroga); requires immediate prophylactic shielding.</li>

              <li><strong>Mature Green Nut Stage (Iri Adike — Months 6–7):</strong> Maximum physical volume reached; shell fiber hardens and interior kernel solidifies into characteristic ruminate grain.</li>

              <li><strong>Ripe Golden Harvest Stage (Kempadike / Dry Chali — Months 8–9):</strong> Complete epicarp color transition to deep saffron-orange. Peak dry-matter accumulation, ideal for processing into commercial supari.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. ICAR-CPCRI Yield Maximization & Crop Protection Protocols</span></h3>

            <p class="dossier-block-text">To sustain high-grade nut clusters and prevent physiological or fungal crop losses:</p>

            <ul class="dossier-bullets">

              <li><strong>Balanced Split NPK Nutrition:</strong> Apply 100 g Nitrogen (220 g Urea), 40 g Phosphorus (200 g Rock Phosphate), and 140 g Potassium (235 g MOP) per bearing palm annually in two equal splits.</li>

              <li><strong>Micronutrient Rectification:</strong> Annual application of Borax (12–15 g) and Zinc Sulphate (20–25 g) per palm to prevent kernel cracking and button shedding.</li>

              <li><strong>Pre-Monsoon Physical Shielding:</strong> Tie 125-gauge virgin polythene hoods (75 × 60 cm) over the bunches before heavy southwest monsoon rains begin.</li>

              <li><strong>Scientific Summer Irrigation:</strong> Deliver 175–200 L of water per palm every 4 to 6 days during dry summer spells (or drip at 16–20 L/palm/day).</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>4. Comparative Trade-offs & Protection Strategies</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>Management Strategy</th><th>Key Advantages (Benefits)</th><th>Key Disadvantages (Limitations)</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">Polythene Bunch Hooding (125-gauge)</td>

                    <td><span class="tag-adv">✓ 100% Chemical-Free:</span> Zero chemical residue on kernels.<br><span class="tag-adv">✓ Complete Barrier:</span> Stops rain-borne fungal zoospores.<br><span class="tag-adv">✓ Single Application:</span> Done once before monsoon season.</td>

                    <td><span class="tag-dis">✗ Skilled Labor:</span> Requires tree climbing to tie each bunch.<br><span class="tag-dis">✗ Condensation Risk:</span> Improper tying can trap internal moisture.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Prophylactic 1% Bordeaux Mixture Spray</td>

                    <td><span class="tag-adv">✓ High Efficacy:</span> Proven broad-spectrum copper barrier.<br><span class="tag-adv">✓ Canopy Coverage:</span> Protects both bunches and upper foliage.</td>

                    <td><span class="tag-dis">✗ Rain Wash-off:</span> Torrential downpours can wash away deposits.<br><span class="tag-dis">✗ Multiple Sprays:</span> Needs 2nd spray 40–45 days later.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Potassium & Micronutrient Fortification</td>

                    <td><span class="tag-adv">✓ Kernel Density:</span> Directly increases dry chali recovery ratio.<br><span class="tag-adv">✓ Thick Pericarp:</span> Naturally enhances resistance to mechanical cracking.</td>

                    <td><span class="tag-dis">✗ Soil Testing Required:</span> Excess K without Mg balance leads to nutrient lock-out.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>5. Commercial Standards & Extension Support</span></h3>

            <p class="dossier-block-text">Commercial quality benchmarks are defined by the <strong>Bureau of Indian Standards (BIS: 2228-1996)</strong> and <strong>Agmark Grading Protocols</strong>. For specialized guidance on high-density nut nutrition, consult <strong>ICAR-CPCRI</strong>, Kasaragod & Regional Station, Vittal.</p>

          </div>

        </div>

      `,

      healthy_leaf: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🍃</span><span>1. Botanical & Foliar Architecture Quality Benchmarks</span></h3>

            <p class="dossier-block-text">Healthy arecanut leaves serve as the primary photosynthetic engine of the palm, dictating annual bunch weight, flowering rate, and disease resilience.</p>

            <ul class="dossier-bullets">

              <li><strong>Crown Frond Count & Balance:</strong> A healthy bearing palm maintains an active canopy of <strong>9 to 12 fully expanded, functional pinnate fronds</strong> arranged in a symmetrical whorl.</li>

              <li><strong>Deep Chlorophyll Pigmentation:</strong> Deep emerald-green to forest-green laminae across all leaflets with balanced chlorophyll-a to chlorophyll-b ratio. Total absence of interveinal chlorosis or bronzing.</li>

              <li><strong>Spindle Spear Vigor:</strong> Central emergent spindle is firm, turgid, standing perfectly erect with smooth pale lime-green sheath. Unblemished by tip-burn or rot.</li>

              <li><strong>Mechanical Elasticity & Cuticle Wax:</strong> Leaflets possess a resilient epicuticular wax layer that minimizes moisture loss and sheds rain droplets rapidly.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚡</span><span>2. Critical Physiological Roles in Palm Longevity & Productivity</span></h3>

            <p class="dossier-block-text">The health of the foliar canopy directly governs commercial yield and tree longevity:</p>

            <ul class="dossier-bullets">

              <li><strong>Primary Carbohydrate Source:</strong> Each frond manufactures photoassimilates feeding <strong>3 to 4 developing nut bunches</strong> simultaneously. Premature loss of even 2 leaves reduces annual bunch weight by <strong>15% to 25%</strong>.</li>

              <li><strong>Vascular Transpiration Engine:</strong> Continuous foliar transpiration pulls vital dissolved calcium, magnesium, and boron upward from lateral roots to the apical meristem.</li>

              <li><strong>Apical Meristem Protection:</strong> Clasping fibrous leaf sheaths wrap tightly around the apical growing point, insulating tender meristem tissue.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🧪</span><span>3. Nutritional Deficiency Diagnostics & Correction Protocols</span></h3>

            <p class="dossier-block-text">Carefully inspect foliar symptoms to address soil imbalances before irreversible damage occurs:</p>

            <ul class="dossier-bullets">

              <li><strong>Nitrogen (N) Deficiency:</strong> Uniform pale green or yellowish fade across the crown. <em>Correction:</em> Apply 220 g Urea per palm in split doses with 12 kg compost.</li>

              <li><strong>Potassium (K) Deficiency:</strong> Orange-yellow translucent spotting and leaflet tip scorching. <em>Correction:</em> Apply 235 g MOP per palm and mulch with husk.</li>

              <li><strong>Magnesium (Mg) Deficiency:</strong> Severe interveinal golden-orange or bronze band on older leaves while midrib remains green. <em>Correction:</em> Apply 150–200 g Magnesium Sulphate or 1 kg Dolomite.</li>

              <li><strong>Boron (B) & Zinc (Zn) Deficiency:</strong> Hooked leaflet tips and stunted spear growth. <em>Correction:</em> Apply 12 g Borax + 20 g Zinc Sulphate around root basin.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>4. Canopy Management & Agronomic Trade-offs (Comparative Analysis)</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>Management Practice</th><th>Key Advantages (Benefits)</th><th>Key Disadvantages (Limitations)</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">Pre-Monsoon Crown Sanitation</td>

                    <td><span class="tag-adv">✓ Disease Prevention:</span> Removes dried sheaths, old spadices, and debris.<br><span class="tag-adv">✓ Pest Control:</span> Destroys breeding niches for bugs and mites.<br><span class="tag-adv">✓ Aeration:</span> Maximizes sunlight penetration into crown.</td>

                    <td><span class="tag-dis">✗ Skilled Labor:</span> Requires experienced tree climbers.<br><span class="tag-dis">✗ Spadix Injury Risk:</span> Accidental damage to emerging inflorescences if careless.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Soil Liming / Dolomite Buffering</td>

                    <td><span class="tag-adv">✓ Acidity Neutralization:</span> Raises pH from acidic 4.5–5.0 to optimal 6.0–6.5.<br><span class="tag-adv">✓ Micronutrient Availability:</span> Unlocks bound phosphorus and stops bronze band.</td>

                    <td><span class="tag-dis">✗ Application Timing:</span> Must be applied 3–4 weeks apart from nitrogen.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">Companion Intercropping (Banana / Cocoa / Pepper)</td>

                    <td><span class="tag-adv">✓ Microclimate Regulation:</span> Protects young fronds against sun scorch.<br><span class="tag-adv">✓ Farm Income:</span> Substantially boosts per-acre net returns.</td>

                    <td><span class="tag-dis">✗ Water Competition:</span> Requires calibrated summer irrigation.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>5. Research Authority & Extension Support</span></h3>

            <p class="dossier-block-text">Canopy diagnostic standards and nutrient management schedules are developed by <strong>ICAR-CPCRI</strong> and the <strong>University of Horticultural Sciences (UHS), Bagalkot</strong>. For localized leaf testing, contact your district Krishi Vigyan Kendra (KVK).</p>

          </div>

        </div>

      `

    },

    kn: {

      mahali: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>೧. ರೋಗಕ್ಕೆ ಕಾರಣಗಳು (ಮೂಲ ಮತ್ತು ಹರಡುವಿಕೆ)</span></h3>

            <p class="dossier-block-text">ಮಹಾಲಿ (ಕರ್ನಾಟಕದಲ್ಲಿ ಕೊಳೆರೋಗ ಎಂದು ಪ್ರಸಿದ್ಧ) ಅತ್ಯಂತ ವಿನಾಶಕಾರಿ <strong><em>Phytophthora meadii</em> McRae</strong> ಎಂಬ ಶಿಲೀಂಧ್ರದಿಂದ ಉಂಟಾಗುತ್ತದೆ.</p>

            <ul class="dossier-bullets">

              <li><strong>ಹವಾಮಾನದ ಪ್ರೇರಕಗಳು:</strong> ನೈಋತ್ಯ ಮುಂಗಾರು ಮಳೆಯ ಕಾಲದಲ್ಲಿ (ಜೂನ್‌ನಿಂದ ಸೆಪ್ಟೆಂಬರ್) ಶೇಕಡಾ ೯೦ ಕ್ಕಿಂತ ಹೆಚ್ಚಿನ ಸಾಪೇಕ್ಷ ಆರ್ದ್ರತೆ, ನಿರಂತರ ಜಿಟಿಜಿಟಿ ಮಳೆ, ಮೋಡ ಕವಿದ ವಾತಾವರಣ, ಮಂದ ಬೆಳಕು ಮತ್ತು ೨೦°C ನಿಂದ ೨೪°C ತಾಪಮಾನ.</li>

              <li><strong>ಹರಡುವ ವಿಧಾನ:</strong> ಮಳೆಯ ಹನಿಗಳು ಶಿಲೀಂಧ್ರದ ಬೀಜಕಗಳನ್ನು ಸಿಡಿಸಿ ಪಕ್ಕದ ಗೊನೆಗಳಿಗೆ ಮತ್ತು ಹತ್ತಿರದ ಮರಗಳಿಗೆ ಸುಲಭವಾಗಿ ಹರಡುತ್ತವೆ.</li>

              <li><strong>ಉಳಿದುಕೊಳ್ಳುವ ಸಾಮರ್ಥ್ಯ:</strong> ಒಣಗಿದ ಕೊಳೆತ ಕಾಯಿಗಳಲ್ಲಿ, ಮರದ ಎಲೆಗಳ ಸಂದುಗಳಲ್ಲಿ ಮತ್ತು ತೋಟದ ನೆಲದಲ್ಲಿ ಬಿದ್ದ ಕಾಯಿಗಳಲ್ಲಿ ಈ ಶಿಲೀಂಧ್ರವು ಮುಂದಿನ ವರ್ಷದವರೆಗೆ ಜೀವಂತವಾಗಿರುತ್ತದೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>೨. ಅಡಿಕೆ ಮರಕ್ಕೆ ಉಂಟಾಗುವ ಪರಿಣಾಮಗಳು (ರೋಗಲಕ್ಷಣಗಳು & ನಷ್ಟ)</span></h3>

            <p class="dossier-block-text">ಸೋಂಕು ಗೊನೆಗಳಲ್ಲಿ ವೇಗವಾಗಿ ಕೊಳೆತವನ್ನು ಉಂಟುಮಾಡುತ್ತದೆ ಮತ್ತು ಮರದ ಕಿರೀಟಕ್ಕೂ ಹರಡಬಹುದು:</p>

            <ul class="dossier-bullets">

              <li><strong>ಆರಂಭಿಕ ಲಕ್ಷಣಗಳು:</strong> ಎಳೆಯ ಅಡಿಕೆಯ ತೊಟ್ಟಿನ ಬಳಿ ನೀರಿನಲ್ಲಿ ನೆನೆದಂತಹ ಕಡು ಹಸಿರು ಅಥವಾ ಕಂದು ಬಣ್ಣದ ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.</li>

              <li><strong>ತೀವ್ರ ಕೊಳೆರೋಗ:</strong> ಬಾಧಿತ ಕಾಯಿಗಳು ಬಣ್ಣ ಕಳೆದುಕೊಂಡು ಉದುರುತ್ತವೆ (ಬಟ್ಟೆ ಉದುರುವಿಕೆ). ಕೆಳಗೆ ಬಿದ್ದ ಕಾಯಿಗಳ ಮೇಲೆ ಹತ್ತಿಯಂತಹ ದಟ್ಟ ಬಿಳಿ ಶಿಲೀಂಧ್ರದ ಬಲೆ ಬೆಳೆಯುತ್ತದೆ.</li>

              <li><strong>ಶಿರ ಕೊಳೆ ರೋಗ (ಸುಳಿ ಕೊಳೆ):</strong> ಮಳೆಯ ನೀರು ಶಿಲೀಂಧ್ರವನ್ನು ಮರದ ಸುಳಿಗೆ ಸಾಗಿಸಿದರೆ, ಮಧ್ಯದ ಸುಳಿ ಕೊಳೆತು ಮರ ಸಂಪೂರ್ಣವಾಗಿ ಒಣಗಿ ಸಾಯುತ್ತದೆ.</li>

              <li><strong>ಆರ್ಥಿಕ ನಷ್ಟ:</strong> ಸೂಕ್ತ ನಿರ್ವಹಣೆ ಮಾಡದಿದ್ದರೆ, ಈ ರೋಗವು ವಾರ್ಷಿಕ ಇಳುವರಿಯ <strong>ಶೇಕಡಾ ೫೦ ರಿಂದ ೯೦ ರಷ್ಟು</strong> ಭಾಗವನ್ನು ನಾಶಪಡಿಸುತ್ತದೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>೩. ರೋಗ ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳು (ICAR-CPCRI ಮಾರ್ಗಸೂಚಿಗಳು)</span></h3>

            <p class="dossier-block-text">ICAR-CPCRI ಸಂಸ್ಥೆಯು ಶಿಫಾರಸು ಮಾಡಿದ ಸಮಗ್ರ ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು:</p>

            <ul class="dossier-bullets">

              <li><strong>೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ:</strong> ೧ ಕೆಜಿ ಮೈಲುತುತ್ತು ಮತ್ತು ೧ ಕೆಜಿ ಸುಣ್ಣವನ್ನು ೧೦೦ ಲೀಟರ್ ನೀರಿನಲ್ಲಿ ಕರಗಿಸಿ ತಯಾರಿಸಿ ಎಲ್ಲಾ ಗೊನೆಗಳಿಗೆ ಸಿಂಪಡಿಸಿ:<br>• <em>ಮೊದಲ ಸಿಂಪಡಣೆ:</em> ಮುಂಗಾರು ಮಳೆ ಆರಂಭವಾಗುವ ಮುನ್ನವೇ (ಮೇ-ಜೂನ್).<br>• <em>ಎರಡನೇ ಸಿಂಪಡಣೆ:</em> ಮಳೆ ಬಿಡುವು ನೀಡಿದಾಗ ೪೦-೪೫ ದಿನಗಳ ನಂತರ (ಜುಲೈ-ಆಗಸ್ಟ್).<br>• <em>ಮೂರನೇ ಸಿಂಪಡಣೆ:</em> ಸೆಪ್ಟೆಂಬರ್ ತಿಂಗಳಲ್ಲೂ ಮಳೆ ಮುಂದುವರಿದರೆ.</li>

              <li><strong>ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ ಕಟ್ಟುವುದು:</strong> ಮಳೆಗಾಲ ಆರಂಭಕ್ಕೆ ಮುನ್ನ ಗೊನೆಗಳಿಗೆ ೧೨೫-ಗೇಜ್ ದಪ್ಪದ ಪಾಲಿಥೀನ್ ಕವರ್ (೭೫ × ೬೦ ಸೆಂ.ಮೀ.) ಕಟ್ಟುವುದು. ಇದು ಮಳೆಯ ಹನಿ ಸೋಕದಂತೆ ೧೦೦% ರಕ್ಷಣೆ ನೀಡುತ್ತದೆ.</li>

              <li><strong>ತೋಟದ ಸ್ವಚ್ಛತೆ:</strong> ನೆಲಕ್ಕೆ ಬಿದ್ದ ಕೊಳೆತ ಕಾಯಿಗಳನ್ನು ಆರಿಸಿ ತೋಟದಿಂದ ಹೊರಗೆ ಹಾಕಿ ಸುಟ್ಟು ನಾಶಪಡಿಸಬೇಕು.</li>

              <li><strong>ಬಸಿಗಾಲುವೆ ನಿರ್ಮಾಣ:</strong> ಮರದ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಸಾಲುಗಳ ನಡುವೆ ೨-೩ ಅಡಿ ಆಳದ ಬಸಿಗಾಲುವೆಗಳನ್ನು ನಿರ್ಮಿಸಬೇಕು.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>೪. ನಿರ್ವಹಣಾ ಕ್ರಮಗಳ ಸಾಧಕ-ಬಾಧಕಗಳ ತುಲನೆ (ಕೋಷ್ಟಕ)</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>ನಿರ್ವಹಣಾ ವಿಧಾನ</th><th>ಮುಖ್ಯ ಅನುಕೂಲಗಳು</th><th>ಮಿತಿಗಳು / ಸವಾಲುಗಳು</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ</td>

                    <td><span class="tag-adv">✓ ಹೆಚ್ಚಿನ ದಕ್ಷತೆ:</span> ಸಾಬೀತಾದ ಶಿಲೀಂಧ್ರನಾಶಕ ರಕ್ಷಣೆ.<br><span class="tag-adv">✓ ಕಡಿಮೆ ವೆಚ್ಚ:</span> ICAR ನಿಂದ ಪ್ರಮಾಣೀಕೃತ ವಿಧಾನ.<br><span class="tag-adv">✓ ವ್ಯಾಪಕ ರಕ್ಷಣೆ:</span> ಇಡೀ ಗೊನೆಯ ಮೇಲ್ಮೈಗೆ ರಕ್ಷಣೆ.</td>

                    <td><span class="tag-dis">✗ ಮಳೆಗೆ ಕೊಚ್ಚಿಹೋಗುವಿಕೆ:</span> ಸಿಂಪಡಿಸಿದ ತಕ್ಷಣ ಭಾರಿ ಮಳೆ ಬಂದರೆ ದ್ರಾವಣ ತೊಳೆದುಹೋಗುತ್ತದೆ.<br><span class="tag-dis">✗ ಕಷ್ಟದ ಶ್ರಮ:</span> ಮರ ಹತ್ತುವ ಕುಶಲ ಕಾರ್ಮಿಕರು ಬೇಕಾಗುತ್ತಾರೆ.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ ಕಟ್ಟುವುದು</td>

                    <td><span class="tag-adv">✓ ರಾಸಾಯನಿಕ ರಹಿತ:</span> ಅಡಿಕೆಯ ಮೇಲೆ ಯಾವುದೇ ಔಷಧಿಯ ಅಂಶವಿಲ್ಲ.<br><span class="tag-adv">✓ ಮಳೆ ನಿರೋಧಕ:</span> ಮಳೆಯ ಹನಿ ನೇರವಾಗಿ ಬೀಳದಂತೆ ಸಂಪೂರ್ಣ ತಡೆ.<br><span class="tag-adv">✓ ಏಕಕಾಲಿಕ ಕೆಲಸ:</span> ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ ಒಮ್ಮೆ ಕಟ್ಟಿದರೆ ಸಾಕು.</td>

                    <td><span class="tag-dis">✗ ಆರಂಭಿಕ ಶ್ರಮ:</span> ಪ್ರತಿಯೊಂದು ಮರವನ್ನು ಹತ್ತಿ ಗೊನೆಗೆ ಕವರ್ ಕಟ್ಟಬೇಕು.<br><span class="tag-dis">✗ ಗಾಳಿಯಾಡದ ಅಪಾಯ:</span> ಸರಿಯಾಗಿ ಕಟ್ಟದಿದ್ದರೆ ಒಳಗಡೆ ತೇವಾಂಶ ನಿಲ್ಲಬಹುದು.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">ತೋಟದ ನೈರ್ಮಲ್ಯ</td>

                    <td><span class="tag-adv">✓ ರೋಗ ನಿಯಂತ್ರಣ:</span> ಶಿಲೀಂಧ್ರದ ಚಕ್ರವನ್ನು ಮುರಿಯುತ್ತದೆ.<br><span class="tag-adv">✓ ಶೂನ್ಯ ಸಾಮಗ್ರಿ ವೆಚ್ಚ:</span> ಯಾವುದೇ ರಾಸಾಯನಿಕಗಳ ಖರೀದಿಯ ಅಗತ್ಯವಿಲ್ಲ.<br><span class="tag-adv">✓ ಶಾಶ್ವತ ಪ್ರಯೋಜನ:</span> ವರ್ಷವಿಡೀ ತೋಟದಲ್ಲಿ ರೋಗದ ಒತ್ತಡ ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ನೆರೆಹೊರೆಯ ಅವಲಂಬನೆ:</span> ಪಕ್ಕದ ತೋಟಗಳಲ್ಲಿ ರೋಗವಿದ್ದರೆ ಗಾಳಿಯ ಮೂಲಕ ಮತ್ತೆ ಬರಬಹುದು.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>೫. ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ ಮತ್ತು ತಾಂತ್ರಿಕ ನೆರವು</span></h3>

            <p class="dossier-block-text">ತಾಂತ್ರಿಕ ಮಾರ್ಗದರ್ಶನ: <strong>ICAR-ಕೇಂದ್ರೀಯ ತೋಟದ ಬೆಳೆಗಳ ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ (CPCRI)</strong> ಕಾಸರಗೋಡು ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಸಂಶೋಧನಾ ಕೇಂದ್ರ ವಿಟ್ಲ, ದಕ್ಷಿಣ ಕನ್ನಡ.<br>ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ನಿಮ್ಮ ತಾಲೂಕಿನ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಅಥವಾ ತೋಟಗಾರಿಕಾ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.</p>

          </div>

        </div>

      `,

      yld: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>೧. ರೋಗಕ್ಕೆ ಕಾರಣಗಳು (ಮೂಲ ಮತ್ತು ಕೀಟ ವಾಹಕಗಳು)</span></h3>

            <p class="dossier-block-text">ಹಳದಿ ಎಲೆ ರೋಗವು (YLD) ಅಡಿಕೆ ಮರದ ಆಹಾರ ನಾಳಗಳಲ್ಲಿ (ಫ್ಲೋಯಂ) ವಾಸಿಸುವ <strong>ಫೈಟೋಪ್ಲಾಸ್ಮಾ (Phytoplasma)</strong> ಎಂಬ ಸೂಕ್ಷ್ಮಾಣುಜೀವಿಯಿಂದ ಉಂಟಾಗುತ್ತದೆ.</p>

            <ul class="dossier-bullets">

              <li><strong>ಕೀಟ ವಾಹಕಗಳು:</strong> ರಸ ಹೀರುವ ಜಿಗಿಹುಳು (<em>Proutista moesta</em>) ಮತ್ತು ಲೇಸ್ ಬಗ್ ಕೀಟಗಳ ಮೂಲಕ ರೋಗಗ್ರಸ್ತ ಮರದಿಂದ ಆರೋಗ್ಯಕರ ಮರಕ್ಕೆ ಹರಡುತ್ತದೆ.</li>

              <li><strong>ಪ್ರೇರಕ ಅಂಶಗಳು:</strong> ಜೌಗು ಪ್ರದೇಶ, ಮಣ್ಣಿನಲ್ಲಿ ಅತಿಯಾದ ಆಮ್ಲೀಯತೆ (ಕಡಿಮೆ pH), ಮತ್ತು ಪೊಟ್ಯಾಶ್/ಮೆಗ್ನೀಸಿಯಮ್ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯು ರೋಗದ ತೀವ್ರತೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತವೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>೨. ಅಡಿಕೆ ಮರಕ್ಕೆ ಉಂಟಾಗುವ ಪರಿಣಾಮಗಳು (ಲಕ್ಷಣಗಳು & ಇಳುವರಿ ಕುಸಿತ)</span></h3>

            <p class="dossier-block-text">ಈ ರೋಗವು ಮರವನ್ನು ಹಂತ ಹಂತವಾಗಿ ಕ್ಷೀಣಗೊಳಿಸುತ್ತದೆ:</p>

            <ul class="dossier-bullets">

              <li><strong>ಎಲೆಗಳ ಹಳದಿ ಬಣ್ಣ:</strong> ಕೆಳಗಿನ ಗರಿಗಳ ಎಲೆಗಳ ತುದಿಯಿಂದ ಗಾಢ ಹಳದಿ ಬಣ್ಣ ಆರಂಭವಾಗಿ ಅಂಚುಗಳ ಉದ್ದಕ್ಕೂ ಹರಡುತ್ತದೆ.</li>

              <li><strong>ಕಿರೀಟ ಕುಗ್ಗುವಿಕೆ:</strong> ಗರಿಗಳು ಚಿಕ್ಕದಾಗಿ, ಗಿಡ್ಡವಾಗಿ ಮುರಿದು ಬೀಳುತ್ತವೆ ಮತ್ತು ಇಡೀ ಮರದ ಕಿರೀಟವು ಕಿರಿದಾಗುತ್ತದೆ.</li>

              <li><strong>ಅಡಿಕೆಯ ಗುಣಮಟ್ಟ ಹಾಳಾಗುವಿಕೆ:</strong> ಕಾಯಿಗಳು ಸಣ್ಣದಾಗುತ್ತವೆ, ಚಾಲಿ ಕಪ್ಪಾಗಿ ಮೆತ್ತಗಾಗುತ್ತದೆ (ಸ್ಪಂಜಿನಂತೆ ಆಗುತ್ತದೆ), ಮಾರಾಟಕ್ಕೆ ಯೋಗ್ಯವಾಗಿರುವುದಿಲ್ಲ.</li>

              <li><strong>ಇಳುವರಿ ನಷ್ಟ:</strong> ೩ ರಿಂದ ೫ ವರ್ಷಗಳಲ್ಲಿ ಇಳುವರಿಯು <strong>ಶೇಕಡಾ ೬೦ ರಿಂದ ೮೦ ರಷ್ಟು</strong> ಕುಸಿಯುತ್ತದೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>೩. ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು (ICAR-CPCRI ಶಿಫಾರಸುಗಳು)</span></h3>

            <p class="dossier-block-text">ಫೈಟೋಪ್ಲಾಸ್ಮಾಕ್ಕೆ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಚಿಕಿತ್ಸೆ ಇಲ್ಲದ ಕಾರಣ, ಮರದ ರೋಗನಿರೋಧಕ ಶಕ್ತಿಯನ್ನು ಹೆಚ್ಚಿಸುವ ಕ್ರಮಗಳನ್ನು ಕೈಗೊಳ್ಳಬೇಕು:</p>

            <ul class="dossier-bullets">

              <li><strong>ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ (NPK):</strong> ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ೧೦೦ ಗ್ರಾಂ ಸಾರಜನಕ (೨೨೦ ಗ್ರಾಂ ಯೂರಿಯಾ), ೪೦ ಗ್ರಾಂ ರಂಜಕ (೨೦೦ ಗ್ರಾಂ ರಾಕ್ ಫಾಸ್ಫೇಟ್), ಮತ್ತು ೧೪೦ ಗ್ರಾಂ ಪೊಟ್ಯಾಶ್ (೨೩೦ ಗ್ರಾಂ ಎಂಒಪಿ) ಅನ್ನು ಎರಡು ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.</li>

              <li><strong>ಸಾವಯವ ಗೊಬ್ಬರ:</strong> ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ೧೨ ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಮತ್ತು ೧೨ ಕೆಜಿ ಹಸಿರೆಲೆ ಗೊಬ್ಬರ ಹಾಕಿ.</li>

              <li><strong>ಬಸಿಗಾಲುವೆ ಸುಧಾರಣೆ:</strong> ಮಳೆಗಾಲದಲ್ಲಿ ಮರದ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಆಳವಾದ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಮಾಡಿ.</li>

              <li><strong>ಮಿಶ್ರ ಬೆಳೆಗಳು:</strong> ತೋಟದಲ್ಲಿ ಕೋಕೋ, ಬಾಳೆ ಮತ್ತು ದ್ವಿದಳ ಧಾನ್ಯದ ಹೊದಿಕೆ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಸಿ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸಿ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>೪. ನಿರ್ವಹಣಾ ಕ್ರಮಗಳ ಸಾಧಕ-ಬಾಧಕಗಳ ತುಲನೆ</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>ನಿರ್ವಹಣಾ ವಿಧಾನ</th><th>ಮುಖ್ಯ ಅನುಕೂಲಗಳು</th><th>ಮಿತಿಗಳು / ಸವಾಲುಗಳು</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">ಪೌಷ್ಟಿಕಾಂಶ ಪುನರುಜ್ಜೀವನ (NPK + ಕಾಂಪೋಸ್ಟ್)</td>

                    <td><span class="tag-adv">✓ ಮರದ ಆಯಸ್ಸು ವೃದ್ಧಿ:</span> ಕಿರೀಟದ ಬೆಳವಣಿಗೆ ಮತ್ತು ಕಾಯಿಯ ತೂಕ ಹೆಚ್ಚಿಸುತ್ತದೆ.<br><span class="tag-adv">✓ ಸುಸ್ಥಿರ ಕೃಷಿ:</span> ಮಣ್ಣಿನ ಉಪಯುಕ್ತ ಸೂಕ್ಷ್ಮಜೀವಿಗಳನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ಸಂಪೂರ್ಣ ಗುಣವಿಲ್ಲ:</span> ಫೈಟೋಪ್ಲಾಸ್ಮಾವನ್ನು ಸಂಪೂರ್ಣ ನಾಶಪಡಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.<br><span class="tag-dis">✗ ದೀರ್ಘಾವಧಿ ಶ್ರಮ:</span> ಚೇತರಿಕೆಗೆ ೨-೩ ವರ್ಷಗಳ ಸತತ ಆರೈಕೆ ಬೇಕು.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">ಬಸಿಗಾಲುವೆ ನಿರ್ಮಾಣ</td>

                    <td><span class="tag-adv">✓ ಬೇರಿನ ಆರೋಗ್ಯ:</span> ಬೇರು ಕೊಳೆಯುವುದನ್ನು ತಪ್ಪಿಸುತ್ತದೆ.<br><span class="tag-adv">✓ ತೇವಾಂಶ ಸಮತೋಲನ:</span> ಮಳೆಗಾಲದಲ್ಲಿ ಮಣ್ಣು ಜೌಗಾಗದಂತೆ ತಡೆಯುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ವೆಚ್ಚ:</span> ಗುಡ್ಡಗಾಡು ಪ್ರದೇಶದಲ್ಲಿ ಕಾಲುವೆ ತೋಡಲು ಹೆಚ್ಚಿನ ವೆಚ್ಚ ತಗಲುತ್ತದೆ.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>೫. ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ ಮತ್ತು ನೆರವು</span></h3>

            <p class="dossier-block-text">ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ <strong>ICAR-CPCRI ತಾಂತ್ರಿಕ ಪ್ರಕಟಣೆ: ಅಡಿಕೆಯ ಹಳದಿ ಎಲೆ ರೋಗ</strong> ನೋಡಿ. ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮತ್ತು ಲಘು ಪೋಷಕಾಂಶಗಳ ಮಾಹಿತಿಗಾಗಿ ನಿಮ್ಮ ಜಿಲ್ಲಾ ತೋಟಗಾರಿಕಾ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.</p>

          </div>

        </div>

      `,

      healthy_nut: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🌰</span><span>೧. ಆರೋಗ್ಯಕರ ಅಡಿಕೆಯ ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳು</span></h3>

            <p class="dossier-block-text">ಆರೋಗ್ಯಕರ ಅಡಿಕೆಯು ಉತ್ತಮ ಕೃಷಿ ನಿರ್ವಹಣೆಯ ಸಂಕೇತವಾಗಿದೆ: ಗಟ್ಟಿಯಾದ ತೊಟ್ಟು, ನಯವಾದ ಸಿಪ್ಪೆ ಮತ್ತು ಘನವಾದ ಸಾಂದ್ರ ಚಾಲಿ ರಚನೆ.</p>

            <ul class="dossier-bullets">

              <li><strong>ಸಿಪ್ಪೆಯ ಸಮಗ್ರತೆ:</strong> ಯಾವುದೇ ಶಿಲೀಂಧ್ರ ಕಲೆಗಳಿಲ್ಲದೆ, ಹೊಳಪಿನ ದಟ್ಟ ಹಸಿರು (ಎಳೆಯ ಅಡಿಕೆ) ಅಥವಾ ಆಕರ್ಷಕ ಕೇಸರಿ ಕಿತ್ತಳೆ ಬಣ್ಣ (ಪಕ್ವ ಅಡಿಕೆ).</li>

              <li><strong>ತೊಟ್ಟಿನ ಹಿಡಿತ:</strong> ಗೊನೆಯಲ್ಲಿ ಕಾಯಿಗಳು ಗಟ್ಟಿಯಾಗಿ ಹಿಡಿದುಕೊಂಡಿರುತ್ತವೆ ಮತ್ತು ಮಳೆಗಾಲದ ಬಿರುಗಾಳಿಗೆ ಸುಲಭವಾಗಿ ಉದುರುವುದಿಲ್ಲ (>೧೮ ನ್ಯೂಟನ್ ಹಿಡಿತ).</li>

              <li><strong>ಚಾಲಿಯ ಸಾಂದ್ರತೆ:</strong> ಅಡಿಕೆಯ ಒಳಭಾಗದಲ್ಲಿ ಅಮೃತಶಿಲೆಯಂತಹ ನೈಸರ್ಗಿಕ ಸುಂದರ ರೇಖೆಗಳು (ರೊಮಿನೇಟ್ ಎಂಡೋಸ್ಪರ್ಮ್), ಶೂನ್ಯ ಟೊಳ್ಳುತನ ಮತ್ತು ಹೆಚ್ಚಿನ ತೂಕ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>📈</span><span>೨. ಅಡಿಕೆ ಬೆಳವಣಿಗೆಯ ೪ ಮುಖ್ಯ ಹಂತಗಳು</span></h3>

            <p class="dossier-block-text">೯ ತಿಂಗಳ ಬೆಳವಣಿಗೆಯ ಹಂತಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು ಸರಿಯಾದ ಆರೈಕೆ ಮತ್ತು ಕಟಾವಿಗೆ ಅತ್ಯಗತ್ಯ:</p>

            <ul class="dossier-bullets">

              <li><strong>ಬಟ್ಟೆ ಅಡಿಕೆ ಹಂತ (ತಿಂಗಳು ೧–೨):</strong> ಹೂವು ಬಿಟ್ಟು ಪರಾಗಸ್ಪರ್ಶವಾದ ನಂತರದ ಪುಟ್ಟ ಕಾಯಿಗಳು. ತೇವಾಂಶ ಮತ್ತು ಬೋರಾನ್ ಕೊರತೆಯಿಂದ ಉದುರುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು.</li>

              <li><strong>ಎಳೆ ಅಡಿಕೆ / ಚಾಲಿ ಹಂತ (ತಿಂಗಳು ೩–೫):</strong> ಕಾಯಿಗಳು ವೇಗವಾಗಿ ಗಾತ್ರ ಪಡೆಯುವ ಹಂತ. ಇದು ಕೊಳೆರೋಗದ ತೀವ್ರತೆಯ ಸಮಯವಾಗಿದ್ದು, ಬೋರ್ಡೋ ಸಿಂಪಡಣೆ ಅಥವಾ ಕವರ್ ಕಟ್ಟುವುದು ಅತ್ಯಗತ್ಯ.</li>

              <li><strong>ಇರಿ ಅಡಿಕೆ ಹಂತ (ತಿಂಗಳು ೬–೭):</strong> ಪೂರ್ಣ ಗಾತ್ರ ತಲುಪಿದ ಹಸಿರು ಕಾಯಿಗಳು. ಒಳಭಾಗದ ಬೀಜ ಗಟ್ಟಿಯಾಗುತ್ತದೆ.</li>

              <li><strong>ಕೆಂಪಡಿಕೆ / ಪಕ್ವ ಕೊಯ್ಲಿನ ಹಂತ (ತಿಂಗಳು ೮–೯):</strong> ಸಿಪ್ಪೆಯು ಸಂಪೂರ್ಣ ಕಿತ್ತಳೆ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುತ್ತದೆ. ಸಂಸ್ಕರಣೆ ಮತ್ತು ಚಾಲಿ ತಯಾರಿಕೆಗೆ ಸೂಕ್ತ ಸಮಯ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>೩. ಇಳುವರಿ ಹೆಚ್ಚಿಸುವ ICAR-CPCRI ಶಿಫಾರಸುಗಳು</span></h3>

            <p class="dossier-block-text">ಅಡಿಕೆ ಗೊನೆಗಳ ಗರಿಷ್ಠ ಇಳುವರಿ ಮತ್ತು ತೂಕವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಲು:</p>

            <ul class="dossier-bullets">

              <li><strong>ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ:</strong> ಪ್ರತಿ ಮರಕ್ಕೆ ೧೦೦ ಗ್ರಾಂ ಸಾರಜನಕ, ೪೦ ಗ್ರಾಂ ರಂಜಕ ಮತ್ತು ೧೪೦ ಗ್ರಾಂ ಪೊಟ್ಯಾಶ್ ಅನ್ನು ಮೇ-ಜೂನ್ ಮತ್ತು ಸೆಪ್ಟೆಂಬರ್-ಅಕ್ಟೋಬರ್‌ನಲ್ಲಿ ನೀಡಿ.</li>

              <li><strong>ಲಘು ಪೋಷಕಾಂಶಗಳ ಪೂರೈಕೆ:</strong> ಕಾಯಿ ಬಿರುಕು ಬಿಡುವುದನ್ನು ಮತ್ತು ಉದುರುವುದನ್ನು ತಡೆಯಲು ವಾರ್ಷಿಕವಾಗಿ ಬೋರಾಕ್ಸ್ (೧೨–೧೫ ಗ್ರಾಂ) ಮತ್ತು ಸತು ಸಲ್ಫೇಟ್ (೨೦–೨೫ ಗ್ರಾಂ) ಹಾಕಿ.</li>

              <li><strong>ಬೇಸಿಗೆ ನೀರಾವರಿ:</strong> ಬೇಸಿಗೆಯಲ್ಲಿ ಪ್ರತಿ ೪-೬ ದಿನಗಳಿಗೊಮ್ಮೆ ಮರಕ್ಕೆ ೧೭೫-೨೦೦ ಲೀಟರ್ ನೀರು ನೀಡಿ (ಅಥವಾ ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ದಿನಕ್ಕೆ ೧೬-೨೦ ಲೀಟರ್).</li>

              <li><strong>ಮಳೆಗಾಲದ ರಕ್ಷಣೆ:</strong> ಮುಂಗಾರು ಆರಂಭಕ್ಕೆ ಮುನ್ನ ೧೨೫-ಗೇಜ್ ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟಿ ಅಥವಾ ೧% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>೪. ರಕ್ಷಣಾ ವಿಧಾನಗಳ ತುಲನೆ</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>ನಿರ್ವಹಣಾ ವಿಧಾನ</th><th>ಮುಖ್ಯ ಪ್ರಯೋಜನಗಳು</th><th>ಮಿತಿಗಳು</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">ಪಾಲಿಥೀನ್ ಕವರ್ ಕಟ್ಟುವುದು</td>

                    <td><span class="tag-adv">✓ ರಾಸಾಯನಿಕ ರಹಿತ:</span> ಅಡಿಕೆಯ ನೈಸರ್ಗಿಕ ಶುದ್ಧತೆ.<br><span class="tag-adv">✓ ಸಂಪೂರ್ಣ ರಕ್ಷಣೆ:</span> ಮಳೆಯ ಹನಿ ತಾಗದಂತೆ ತಡೆಯುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ಶ್ರಮ:</span> ಪ್ರತಿ ಮರವನ್ನು ಹತ್ತಿ ಕಟ್ಟಬೇಕು.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ</td>

                    <td><span class="tag-adv">✓ ಸಾಬೀತಾದ ರಕ್ಷಣೆ:</span> ಶಿಲೀಂಧ್ರ ತಡೆಗೋಡೆ ನಿರ್ಮಿಸುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ಮಳೆ ತೊಳೆಯುವಿಕೆ:</span> ಭಾರೀ ಮಳೆಗೆ ತೊಳೆದುಹೋಗಬಹುದು.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>೫. ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳು ಮತ್ತು ತಜ್ಞರ ನೆರವು</span></h3>

            <p class="dossier-block-text">ಅಡಿಕೆ ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳನ್ನು <strong>ಭಾರತೀಯ ಗುಣಮಟ್ಟ ಬ್ಯೂರೋ (BIS: 2228-1996)</strong> ಮತ್ತು <strong>ಅಗ್‌ಮಾರ್ಕ್</strong> ನಿಗದಿಪಡಿಸಿದೆ. ಹೆಚ್ಚಿನ ತಾಂತ್ರಿಕ ವಿವರಗಳಿಗಾಗಿ ICAR-CPCRI ಕಾಸರಗೋಡು ಮತ್ತು ವಿಟ್ಲ ಕೇಂದ್ರಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ.</p>

          </div>

        </div>

      `,

      healthy_leaf: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🍃</span><span>೧. ಆರೋಗ್ಯಕರ ಗರಿಗಳ ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳು</span></h3>

            <p class="dossier-block-text">ಆರೋಗ್ಯಕರ ಗರಿಗಳು ಅಡಿಕೆ ಮರದ ಆಹಾರ ತಯಾರಿಕೆಯ ಮುಖ್ಯ ಎಂಜಿನ್ ಆಗಿದ್ದು, ಇಳುವರಿ ಮತ್ತು ಮರದ ಆಯಸ್ಸನ್ನು ನಿರ್ಧರಿಸುತ್ತವೆ.</p>

            <ul class="dossier-bullets">

              <li><strong>ಗರಿಗಳ ಸಂಖ್ಯೆ:</strong> ಒಂದು ಆರೋಗ್ಯಕರ ಫಲ ನೀಡುವ ಅಡಿಕೆ ಮರದಲ್ಲಿ <strong>೯ ರಿಂದ ೧೨ ಸಂಪೂರ್ಣ ಹಸಿರು ಗರಿಗಳು</strong> ಸುಂದರವಾಗಿ ಹರಡಿರಬೇಕು.</li>

              <li><strong>ಕ್ಲೋರೋಫಿಲ್ ವರ್ಣದ್ರವ್ಯ:</strong> ಎಲೆಗಳು ಯಾವುದೇ ಹಳದಿ ಅಥವಾ ಕಂದು ಕಲೆಗಳಿಲ್ಲದೆ ಗಾಢ ಹಸಿರು ಬಣ್ಣವನ್ನು ಹೊಂದಿರಬೇಕು.</li>

              <li><strong>ಸುಳಿಯ ಆರೋಗ್ಯ:</strong> ಮಧ್ಯದ ಸುಳಿಯು ನೇರವಾಗಿ, ದೃಢವಾಗಿ ಮತ್ತು ತಿಳಿ ಹಸಿರು ಬಣ್ಣದೊಂದಿಗೆ ರೋಗರಹಿತವಾಗಿರಬೇಕು.</li>

              <li><strong>ಮೇಣದ ರಕ್ಷಣಾ ಪದರ:</strong> ಎಲೆಗಳ ಮೇಲ್ಮೈಯಲ್ಲಿ ನೈಸರ್ಗಿಕ ಮೇಣದ ಪದರವಿದ್ದು, ನೀರಿನ ಹನಿಗಳು ನಿಲ್ಲದಂತೆ ಜಾರಿಸುತ್ತವೆ ಮತ್ತು ಗಾಳಿಗೆ ಸ್ಥಿತಿಸ್ಥಾಪಕತ್ವ ನೀಡುತ್ತವೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚡</span><span>೨. ಗರಿಗಳ ಪ್ರಮುಖ ಜೈವಿಕ ಪಾತ್ರಗಳು</span></h3>

            <p class="dossier-block-text">ಗರಿಗಳ ಆರೋಗ್ಯವು ತೋಟದ ಆದಾಯವನ್ನು ನೇರವಾಗಿ ನಿರ್ಧರಿಸುತ್ತದೆ:</p>

            <ul class="dossier-bullets">

              <li><strong>ಆಹಾರ ಉತ್ಪಾದನೆ:</strong> ಪ್ರತಿ ಗರಿಯು ಏಕಕಾಲದಲ್ಲಿ <strong>೩ ರಿಂದ ೪ ಬೆಳೆಯುತ್ತಿರುವ ಗೊನೆಗಳಿಗೆ</strong> ಆಹಾರ ಪೂರೈಸುತ್ತದೆ. ಕೇವಲ ೨ ಗರಿಗಳು ನಷ್ಟವಾದರೂ ವಾರ್ಷಿಕ ಇಳುವರಿಯಲ್ಲಿ <strong>೧೫% ರಿಂದ ೨೫% ಕುಸಿತ</strong> ಉಂಟಾಗುತ್ತದೆ.</li>

              <li><strong>ನೀರು ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ಹೀರುವಿಕೆ:</strong> ಎಲೆಗಳ ಬಾಷ್ಪೀಭವನ ಕ್ರಿಯೆಯು ಬೇರುಗಳಿಂದ ಕ್ಯಾಲ್ಸಿಯಂ, ಮೆಗ್ನೀಸಿಯಮ್ ಮತ್ತು ಬೋರಾನ್ ಅನ್ನು ಮರದ ತುದಿಯವರೆಗೆ ಸೆಳೆಯುತ್ತದೆ.</li>

              <li><strong>ಸುಳಿಯ ರಕ್ಷಣೆ:</strong> ಎಲೆಗಳ ದಪ್ಪನೆಯ ತೊಗಲು ಮರದ ಸೂಕ್ಷ್ಮ ಸುಳಿಯನ್ನು ತೀವ್ರ ಬಿಸಿಲು ಮತ್ತು ಕೀಟಗಳಿಂದ ರಕ್ಷಿಸುತ್ತದೆ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🧪</span><span>೩. ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯ ಲಕ್ಷಣಗಳು & ಪರಿಹಾರಗಳು</span></h3>

            <p class="dossier-block-text">ಗರಿಗಳಲ್ಲಿನ ಲಕ್ಷಣಗಳನ್ನು ನೋಡಿ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶದ ಸಮತೋಲನವನ್ನು ಸರಿಪಡಿಸಿ:</p>

            <ul class="dossier-bullets">

              <li><strong>ಸಾರಜನಕ ಕೊರತೆ:</strong> ಇಡೀ ಕಿರೀಟವು ತೆಳು ಹಸಿರು ಅಥವಾ ಹಳದಿಯಾಗುವುದು. <em>ಪರಿಹಾರ:</em> ಮರಕ್ಕೆ ೨೨೦ ಗ್ರಾಂ ಯೂರಿಯಾ ಮತ್ತು ೧೨ ಕೆಜಿ ಕಾಂಪೋಸ್ಟ್ ಹಾಕಿ.</li>

              <li><strong>ಪೊಟ್ಯಾಶ್ ಕೊರತೆ:</strong> ಎಲೆಗಳ ತುದಿ ಸುಟ್ಟಂತೆ ಕಾಣುವುದು ಮತ್ತು ಕಿತ್ತಳೆ ಚುಕ್ಕೆಗಳು. <em>ಪರಿಹಾರ:</em> ಮರಕ್ಕೆ ೨೩೫ ಗ್ರಾಂ ಎಂಒಪಿ ನೀಡಿ ಮತ್ತು ಅಡಿಕೆ ಸಿಪ್ಪೆಯ ಮಲ್ಚಿಂಗ್ ಮಾಡಿ.</li>

              <li><strong>ಮೆಗ್ನೀಸಿಯಮ್ ಕೊರತೆ:</strong> ಎಲೆಯ ಮಧ್ಯದ ನರ ಹಸಿರಾಗಿದ್ದು ಪಕ್ಕದ ಭಾಗ ಬಂಗಾರದ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುವುದು. <em>ಪರಿಹಾರ:</em> ಮರಕ್ಕೆ ೧೫೦-೨೦೦ ಗ್ರಾಂ ಮೆಗ್ನೀಸಿಯಮ್ ಸಲ್ಫೇಟ್ ಅಥವಾ ೧ ಕೆಜಿ ಡಾಲಮೈಟ್ ಹಾಕಿ.</li>

              <li><strong>ಬೋರಾನ್ ಮತ್ತು ಸತು ಕೊರತೆ:</strong> ಎಲೆಗಳ ತುದಿ ಕೊಕ್ಕೆಯಂತೆ ಬಾಗುವುದು ಮತ್ತು ಸುಳಿ ಗಿಡ್ಡವಾಗುವುದು. <em>ಪರಿಹಾರ:</em> ೧೨ ಗ್ರಾಂ ಬೋರಾಕ್ಸ್ ಮತ್ತು ೨೦ ಗ್ರಾಂ ಸತು ಸಲ್ಫೇಟ್ ನೀಡಿ.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>೪. ಕಿರೀಟ ನಿರ್ವಹಣಾ ವಿಧಾನಗಳ ತುಲನೆ</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead>

                  <tr><th>ನಿರ್ವಹಣಾ ವಿಧಾನ</th><th>ಮುಖ್ಯ ಅನುಕೂಲಗಳು</th><th>ಮಿತಿಗಳು</th></tr>

                </thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">ಮಳೆಗಾಲ ಪೂರ್ವ ಕಿರೀಟ ಸ್ವಚ್ಛತೆ</td>

                    <td><span class="tag-adv">✓ ರೋಗ ತಡೆ:</span> ಒಣಗಿದ ಎಲೆ, ಸಿಂಗಾರ ಮತ್ತು ಶಿಲೀಂಧ್ರ ಕಲ್ಮಶಗಳನ್ನು ತೆಗೆಯುತ್ತದೆ.<br><span class="tag-adv">✓ ಗಾಳಿಯಾಡುವಿಕೆ:</span> ಕಿರೀಟಕ್ಕೆ ಉತ್ತಮ ಸೂರ್ಯನ ಬೆಳಕು ಬೀಳುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ಕುಶಲ ಕಾರ್ಮಿಕರು:</span> ನುರಿತ ಮರ ಹತ್ತುವವರು ಬೇಕು.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">ಸುಣ್ಣ / ಡಾಲಮೈಟ್ ಬಳಕೆ</td>

                    <td><span class="tag-adv">✓ ಆಮ್ಲೀಯತೆ ನಿವಾರಣೆ:</span> ಮಣ್ಣಿನ pH ಮಟ್ಟವನ್ನು ಉತ್ತಮಗೊಳಿಸುತ್ತದೆ.<br><span class="tag-adv">✓ ಪೋಷಕಾಂಶ ಬಿಡುಗಡೆ:</span> ರಂಜಕವನ್ನು ಸುಲಭವಾಗಿ ಹೀರಿಕೊಳ್ಳಲು ನೆರವಾಗುತ್ತದೆ.</td>

                    <td><span class="tag-dis">✗ ಸಮಯದ ಅಂತರ:</span> ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ ನೀಡುವ ೩-೪ ವಾರಗಳ ಮೊದಲು ಹಾಕಬೇಕು.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>೫. ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ ಮತ್ತು ನೆರವು</span></h3>

            <p class="dossier-block-text">ಗರಿಗಳ ಆರೋಗ್ಯ ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ನಿರ್ವಹಣಾ ವೇಳಾಪಟ್ಟಿಯನ್ನು <strong>ICAR-CPCRI</strong> ಮತ್ತು <strong>ತೋಟಗಾರಿಕಾ ವಿಜ್ಞಾನಗಳ ವಿಶ್ವವಿದ್ಯಾಲಯ (UHS), ಬಾಗಲಕೋಟೆ</strong> ಅಭಿವೃದ್ಧಿಪಡಿಸಿವೆ. ಎಲೆ ಪರೀಕ್ಷೆಗಾಗಿ ನಿಮ್ಮ ಜಿಲ್ಲಾ KVK ಸಂಪರ್ಕಿಸಿ.</p>

          </div>

        </div>

      `

    },

    hi: {

      mahali: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>१. रोग के कारण (इटियोलॉजी एवं फैलाव)</span></h3>

            <p class="dossier-block-text">महाली (कोलेरोगा) अत्यंत विनाशकारी <strong><em>Phytophthora meadii</em> McRae</strong> कवक द्वारा होता है।</p>

            <ul class="dossier-bullets">

              <li><strong>जलवायु परिस्थितियाँ:</strong> दक्षिण-पश्चिम मानसून (जून से सितंबर) के दौरान उच्च आर्द्रता (>90%), लगातार बारिश, बादल छाए रहना और 20°C से 24°C तापमान।</li>

              <li><strong>प्रसार का तरीका:</strong> बारिश की बौछारें कवक बीजाणुओं को आसपास के गुच्छों और पड़ोसी पेड़ों तक आसानी से फैलाती हैं।</li>

              <li><strong>जीवित रहने की क्षमता:</strong> सूखे सड़े हुए फलों, पेड़ की दरारों और जमीन पर गिरे फलों में कवक लंबे समय तक जीवित रहता है।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>२. पौधे पर प्रभाव (लक्षण एवं फसल क्षति)</span></h3>

            <p class="dossier-block-text">संक्रमण गुच्छों में तेजी से सड़न पैदा करता है और पेड़ के मुकुट को भी नष्ट कर सकता है:</p>

            <ul class="dossier-bullets">

              <li><strong>प्रारंभिक लक्षण:</strong> फलों के डंठल के पास जल-सिक्त गहरे हरे या भूरे धब्बे दिखाई देते हैं।</li>

              <li><strong>गंभीर फल सड़न:</strong> संक्रमित फल तेजी से काले पड़ते हैं और भारी मात्रा में गिरते हैं। गिरे हुए फलों पर घनी सफेद कवक की परत बन जाती है।</li>

              <li><strong>बड रॉट (शीर्ष सड़न):</strong> यदि बारिश कवक को केंद्रीय कोपल में ले जाती है, तो पेड़ का शीर्ष सड़ जाता है और पेड़ मर जाता है।</li>

              <li><strong>आर्थिक क्षति:</strong> अनुपचारित बागानों में <strong>50% से 90%</strong> तक फसल बर्बाद हो जाती है।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>३. रोकथाम एवं प्रबंधन (ICAR-CPCRI प्रोटोकॉल)</span></h3>

            <p class="dossier-block-text">ICAR-CPCRI द्वारा प्रमाणित एकीकृत प्रबंधन उपाय:</p>

            <ul class="dossier-bullets">

              <li><strong>1% बोर्डो मिश्रण छिड़काव:</strong> 1 किग्रा कॉपर सल्फेट + 1 किग्रा बुझा चूना 100 लीटर पानी में मिलाकर गुच्छों पर छिड़कें:<br>• <em>पहला छिड़काव:</em> मानसून शुरू होने से ठीक पहले (मई-जून)।<br>• <em>दूसरा छिड़काव:</em> 40-45 दिनों के बाद वर्षा विराम के दौरान।<br>• <em>तीसरा छिड़काव:</em> यदि सितंबर तक वर्षा जारी रहे।</li>

              <li><strong>पॉलीथीन से गुच्छे ढकना:</strong> मानसून से पहले गुच्छों पर 125-गेज पॉलीथीन कवर (75 × 60 सेमी) बाँधें। यह वर्षा से पूरी सुरक्षा देता है।</li>

              <li><strong>बागान स्वच्छता:</strong> गिरे हुए सभी सड़े फलों को इकट्ठा करके जला दें।</li>

              <li><strong>जल निकासी:</strong> जड़ों के पास पानी जमा न होने देने के लिए 2-3 फीट गहरी नालियाँ बनाएँ।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>४. प्रबंधन रणनीतियों की तुलना (सारणी)</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead><tr><th>रणनीति</th><th>प्रमुख लाभ</th><th>सीमाएँ</th></tr></thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">1% बोर्डो मिश्रण छिड़काव</td>

                    <td><span class="tag-adv">✓ उच्च प्रभावशीलता:</span> प्रमाणित कवकनाशी सुरक्षा।<br><span class="tag-adv">✓ किफायती:</span> ICAR का मानक उपाय।</td>

                    <td><span class="tag-dis">✗ बारिश में धुलना:</span> छिड़काव के तुरंत बाद भारी वर्षा से धुल सकता है।<br><span class="tag-dis">✗ श्रमसाध्य:</span> कुशल पेड़ चढ़ने वालों की आवश्यकता।</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">पॉलीथीन बैग आवरण</td>

                    <td><span class="tag-adv">✓ रसायन मुक्त:</span> फलों पर कोई अवशेष नहीं।<br><span class="tag-adv">✓ वर्षा अवरोधक:</span> वर्षा की बूंदों को पूरी तरह रोकता है।</td>

                    <td><span class="tag-dis">✗ श्रमसाध्य:</span> प्रत्येक पेड़ पर चढ़कर बाँधना पड़ता है।</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>५. अनुसंधान संस्थान एवं सहायता</span></h3>

            <p class="dossier-block-text">मार्गदर्शन: <strong>ICAR-केंद्रीय रोपण फसल अनुसंधान संस्थान (CPCRI)</strong>, कासरगोड, केरल एवं विट्टल, कर्नाटक। अपने स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।</p>

          </div>

        </div>

      `,

      yld: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>१. रोग के कारण (फाइटोप्लाज्मा एवं कीट वाहक)</span></h3>

            <p class="dossier-block-text">पीला पत्ता रोग (YLD) फ्लोएम ऊतक में रहने वाले <strong>फाइटोप्लाज्मा</strong> सूक्ष्मजीवों से होता है।</p>

            <ul class="dossier-bullets">

              <li><strong>कीट वाहक:</strong> रस चूसने वाले पादप फुदके (<em>Proutista moesta</em>) द्वारा फैलता है।</li>

              <li><strong>सहायक कारक:</strong> जलभराव, मिट्टी की अम्लीयता (कम pH), और पोटाश/मैग्नीशियम की कमी।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>२. पौधे पर प्रभाव एवं लक्षण</span></h3>

            <p class="dossier-block-text">यह रोग पेड़ को धीरे-धीरे कमजोर करता है:</p>

            <ul class="dossier-bullets">

              <li><strong>पत्तियों का पीलापन:</strong> पत्तियों के सिरों से शुरू होकर पीलापन फैलता है।</li>

              <li><strong>मुकुट का सिकुड़ना:</strong> पत्तियाँ छोटी, भंगुर हो जाती हैं और पेड़ का शीर्ष सिकुड़ जाता है।</li>

              <li><strong>फल की गुणवत्ता में गिरावट:</strong> फल छोटे हो जाते हैं और गिरी अंदर से काली व स्पंजी हो जाती है।</li>

              <li><strong>उपज में कमी:</strong> 3 से 5 वर्षों में उपज <strong>60% से 80%</strong> तक गिर जाती है।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>३. ICAR-CPCRI प्रबंधन रणनीतियाँ</span></h3>

            <p class="dossier-block-text">रोग प्रतिरोधक क्षमता बढ़ाने हेतु अनुशंसित उपाय:</p>

            <ul class="dossier-bullets">

              <li><strong>संतुलित पोषण (NPK):</strong> प्रति वृक्ष प्रति वर्ष 100 ग्राम नाइट्रोजन, 40 ग्राम फॉस्फोरस, और 140 ग्राम पोटाश दो किश्तों में दें।</li>

              <li><strong>जैविक खाद:</strong> प्रति वृक्ष 12 किग्रा गोबर की खाद और 12 किग्रा हरी पत्ती की खाद डालें।</li>

              <li><strong>जल निकासी:</strong> मानसून में पानी जमा न होने देने के लिए गहरी नालियाँ बनाएँ।</li>

              <li><strong>अंतरफसलें:</strong> मिट्टी की उर्वरता बढ़ाने के लिए कोको और केला लगाएँ।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>४. प्रबंधन रणनीतियों की तुलना</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead><tr><th>विधि</th><th>लाभ</th><th>सीमाएँ</th></tr></thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">संतुलित पोषण (NPK + खाद)</td>

                    <td><span class="tag-adv">✓ पेड़ की जीवन अवधि:</span> पत्तियों के विकास और फलों के वजन में सुधार।</td>

                    <td><span class="tag-dis">✗ पूर्ण उपचार नहीं:</span> फाइटोप्लाज्मा को पूरी तरह नष्ट नहीं कर सकता।</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>५. अनुसंधान संस्थान एवं सहायता</span></h3>

            <p class="dossier-block-text">तकनीकी विवरण हेतु <strong>ICAR-CPCRI</strong> कासरगोड से संपर्क करें।</p>

          </div>

        </div>

      `,

      healthy_nut: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🌰</span><span>१. स्वस्थ सुपारी के गुणवत्ता मानक</span></h3>

            <p class="dossier-block-text">स्वस्थ सुपारी अच्छे प्रबंधन का प्रतीक है: मजबूत डंठल पकड़, स्वच्छ छिलका और ठोस आंतरिक गिरी।</p>

            <ul class="dossier-bullets">

              <li><strong>छिलके की अखंडता:</strong> चमकदार गहरा हरा या गहरा नारंगी रंग, बिना किसी कवक धब्बे के।</li>

              <li><strong>मजबूत डंठल:</strong> फलों का गुच्छा पेड़ से मजबूती से जुड़ा रहता है और आसानी से नहीं गिरता।</li>

              <li><strong>ठोस आंतरिक गिरी:</strong> सुंदर संगमरमर जैसी नक्काशीदार गिरी, शून्य खोखलापन और उच्च विशिष्ट गुरुत्व।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>📈</span><span>२. विकास के ४ प्रमुख चरण</span></h3>

            <p class="dossier-block-text">उचित प्रबंधन और कटाई के लिए 9 महीने के चक्र को समझना आवश्यक है:</p>

            <ul class="dossier-bullets">

              <li><strong>बट्टे अडिके (माह 1-2):</strong> परागण के बाद का शुरुआती चरण। बोरॉन की कमी से गिरने की संभावना।</li>

              <li><strong>कच्ची चाली सुपारी (माह 3-5):</strong> फल के तेजी से बढ़ने का समय। महाली रोग से बचाव हेतु छिड़काव का समय।</li>

              <li><strong>पकी हरी सुपारी (माह 6-7):</strong> पूर्ण आकार प्राप्त सुपारी, गिरी अंदर से ठोस होना शुरू होती है।</li>

              <li><strong>पकी सूखी चाली (माह 8-9):</strong> छिलका नारंगी हो जाता है। प्रसंस्करण और व्यापार के लिए उपयुक्त।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>३. उपज संवर्धन के उपाय (ICAR-CPCRI)</span></h3>

            <p class="dossier-block-text">उच्च गुणवत्ता और अधिक उपज बनाए रखने के लिए:</p>

            <ul class="dossier-bullets">

              <li><strong>संतुलित उर्वरक:</strong> 100 ग्राम नाइट्रोजन, 40 ग्राम फॉस्फोरस, 140 ग्राम पोटाश प्रति वृक्ष।</li>

              <li><strong>सूक्ष्म पोषक तत्व:</strong> फलों के फटने को रोकने के लिए बोरेक्स (12-15 ग्राम) और जिंक सल्फेट (20-25 ग्राम)।</li>

              <li><strong>गर्मी में सिंचाई:</strong> गर्मियों में प्रति 4-6 दिन में 175-200 लीटर पानी प्रति पेड़ दें।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>४. मानक एवं सहायता</span></h3>

            <p class="dossier-block-text">गुणवत्ता मानक <strong>BIS: 2228-1996</strong> और <strong>Agmark</strong> द्वारा निर्धारित हैं। परामर्श हेतु ICAR-CPCRI से संपर्क करें।</p>

          </div>

        </div>

      `,

      healthy_leaf: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🍃</span><span>१. स्वस्थ पत्तियों के गुणवत्ता मानक</span></h3>

            <p class="dossier-block-text">पत्तियाँ सुपारी के पेड़ का मुख्य भोजन निर्माण अंग हैं, जो वार्षिक उपज और पेड़ के स्वास्थ्य को निर्धारित करती हैं।</p>

            <ul class="dossier-bullets">

              <li><strong>पत्तियों की संख्या:</strong> स्वस्थ फलदायी पेड़ में <strong>९ से १२ हरी पत्तियाँ</strong> संतुलित मुकुट में होनी चाहिए।</li>

              <li><strong>गहरा क्लोरोफिल:</strong> पत्तियाँ किसी भी पीलेपन के बिना चमकदार गहरे हरे रंग की होनी चाहिए।</li>

              <li><strong>मजबूत कोपल:</strong> केंद्रीय कोपल सीधी, मजबूत और हल्के हरे रंग की होनी चाहिए।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚡</span><span>२. पत्तियों की जैविक भूमिकाएँ</span></h3>

            <ul class="dossier-bullets">

              <li><strong>भोजन निर्माण:</strong> प्रत्येक पत्ती एक साथ <strong>३ से ४ गुच्छों</strong> को भोजन प्रदान करती है। केवल 2 पत्तियों के नुकसान से उपज में <strong>15% से 25% गिरावट</strong> आ सकती है।</li>

              <li><strong>पोषक तत्व परिवहन:</strong> पत्तियों का वाष्पोत्सर्जन जड़ों से कैल्शियम और मैग्नीशियम को शीर्ष तक खींचता है।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🧪</span><span>३. पोषक तत्वों की कमी के लक्षण</span></h3>

            <ul class="dossier-bullets">

              <li><strong>नाइट्रोजन की कमी:</strong> पूरी पत्ती का हल्का पीला पड़ना। <em>उपाय:</em> यूरिया 220 ग्राम + खाद दें।</li>

              <li><strong>पोटाश की कमी:</strong> किनारों का जलना। <em>उपाय:</em> 235 ग्राम MOP दें और छिलके की मल्चिंग करें।</li>

              <li><strong>मैग्नीशियम की कमी:</strong> पुरानी पत्तियों पर नारंगी-पीली पट्टी। <em>उपाय:</em> डोलोमाइट या मैग्नीशियम सल्फेट दें।</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>४. अनुसंधान संस्थान</span></h3>

            <p class="dossier-block-text">तकनीकी मार्गदर्शन: <strong>ICAR-CPCRI</strong> और <strong>बागवानी विज्ञान विश्वविद्यालय (UHS), बागलकोट</strong>।</p>

          </div>

        </div>

      `

    },

    ml: {

      mahali: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>1. രോഗകാരണങ്ങൾ (ഉത്ഭവവും വ്യാപനവും)</span></h3>

            <p class="dossier-block-text">മഹാലി അഥവാ കൊളെറോഗ <strong><em>Phytophthora meadii</em> McRae</strong> എന്ന അതിവിനാശകാരിയായ കുമിൾ മൂലമുണ്ടാകുന്നു.</p>

            <ul class="dossier-bullets">

              <li><strong>കാലാവസ്ഥ ഘടകങ്ങൾ:</strong> ഇടവപ്പാതിയിലെ (ജൂൺ-സെപ്റ്റംബർ) ഉയർന്ന ആപേക്ഷിക ഈർപ്പം (>90%), തുടർച്ചയായ മഴ, മൂടിയ ആകാശം, 20°C മുതൽ 24°C വരെയുള്ള താപനില.</li>

              <li><strong>രോഗപ്പകർച്ച:</strong> മഴത്തുള്ളികൾ തെറിച്ച് കുമിൾ വിത്തുകൾ അടുത്തുള്ള കുലകളിലേക്കും മരങ്ങളിലേക്കും വേഗത്തിൽ പടരുന്നു.</li>

              <li><strong>അതിജീവനം:</strong> ഉണങ്ങിയ അടക്കകളിലും തോട്ടത്തിലെ അവശിഷ്ടങ്ങളിലും ഈ കുമിൾ ദീർഘകാലം നിലനിൽക്കുന്നു.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>2. ലക്ഷണങ്ങളും വിളനാശവും</span></h3>

            <p class="dossier-block-text">അടക്കക്കുലകളിൽ അതിവേഗം ചീയലുണ്ടാക്കുകയും മണ്ടയെ ബാധിക്കുകയും ചെയ്യുന്നു:</p>

            <ul class="dossier-bullets">

              <li><strong>പ്രാഥമിക ലക്ഷണങ്ങൾ:</strong> ഇളം അടക്കകളുടെ ഞെട്ടിന് സമീപം വെള്ളം നനഞ്ഞ കറുത്ത പാടുകൾ കാണപ്പെടുന്നു.</li>

              <li><strong>കായ്ചീയൽ:</strong> അടക്കകൾ കൊഴിഞ്ഞു വീഴുന്നു. വീണുകിടക്കുന്ന അടക്കകളിൽ പഞ്ഞി പോലുള്ള വെളുത്ത പൂപ്പൽ വളരുന്നു.</li>

              <li><strong>മണ്ട ചീയൽ:</strong> മഴവെള്ളം വഴി കുമിൾ മണ്ടയിലെത്തിയാൽ കുരുത്തോല ചീഞ്ഞ് തെങ്ങ് പൂർണ്ണമായി നശിക്കുന്നു.</li>

              <li><strong>വിളനഷ്ടം:</strong> നിയന്ത്രിച്ചില്ലെങ്കിൽ <strong>50% മുതൽ 90% വരെ</strong> വിളനഷ്ടം സംഭവിക്കാം.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. പ്രതിരോധ മാർഗ്ഗങ്ങൾ (ICAR-CPCRI)</span></h3>

            <p class="dossier-block-text">സിപിസിആർഐ ശുപാർശ ചെയ്യുന്ന സംയോജിത പ്രതിരോധ മാർഗ്ഗങ്ങൾ:</p>

            <ul class="dossier-bullets">

              <li><strong>1% ബോർഡോ മിശ്രിതം തളിക്കുക:</strong> 1 കിലോഗ്രാം തുരിശും 1 കിലോഗ്രാം ചുണ്ണാമ്പും 100 ലിറ്റർ വെള്ളത്തിൽ കലക്കി കുലകളിൽ തളിക്കുക:<br>• <em>ആദ്യ തളിക്കൽ:</em> കാലവർഷത്തിന് മുൻപ് (മെയ്-ജൂൺ).<br>• <em>രണ്ടാം തളിക്കൽ:</em> 40-45 ദിവസങ്ങൾക്ക് ശേഷം മഴ മാറുന്ന സമയത്ത്.<br>• <em>മൂന്നാം തളിക്കൽ:</em> സെപ്റ്റംബർ വരെ മഴ തുടരുകയാണെങ്കിൽ.</li>

              <li><strong>പോളിത്തീൻ കവറിംഗ്:</strong> മഴയ്ക്ക് മുൻപ് കുലകളിൽ 125-ഗേജ് പോളിത്തീൻ ഷീറ്റ് (75 × 60 സെ.മീ.) കെട്ടുക. ഇത് മഴത്തുള്ളികൾ പതിക്കുന്നത് തടഞ്ഞ് പൂർണ്ണ സംരക്ഷണം നൽകുന്നു.</li>

              <li><strong>തോട്ടം ശുചീകരണം:</strong> കൊഴിഞ്ഞുവീണ അടക്കകൾ പെറുക്കി തീയിട്ട് നശിപ്പിക്കുക.</li>

              <li><strong>നീർവാർച്ച:</strong> വേരുകളിൽ വെള്ളം കെട്ടിനിൽക്കാതിരിക്കാൻ ചാലുകൾ കീറുക.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚖️</span><span>4. പ്രതിരോധ മാർഗ്ഗങ്ങളുടെ താരതമ്യം</span></h3>

            <div class="tradeoff-table-wrap">

              <table class="tradeoff-table">

                <thead><tr><th>മാർഗ്ഗം</th><th>പ്രയോജനങ്ങൾ</th><th>പരിമിതികൾ</th></tr></thead>

                <tbody>

                  <tr>

                    <td class="strategy-name">1% ബോർഡോ മിശ്രിതം തളിക്കൽ</td>

                    <td><span class="tag-adv">✓ ഫലപ്രദം:</span> തെളിയിക്കപ്പെട്ട കുമിൾനാശിനി സംരക്ഷണം.<br><span class="tag-adv">✓ ചെലവ് കുറവ്:</span> ലളിതവും കാര്യക്ഷമവുമായ രീതി.</td>

                    <td><span class="tag-dis">✗ മഴയിൽ ഒലിച്ചുപോകൽ:</span> കനത്ത മഴയിൽ മരുന്ന് ഒലിച്ചുപോകാൻ സാധ്യതയുണ്ട്.</td>

                  </tr>

                  <tr>

                    <td class="strategy-name">പോളിത്തീൻ കവറിംഗ്</td>

                    <td><span class="tag-adv">✓ വിഷരഹിതം:</span> അടക്കയിൽ മരുന്നുകളുടെ അംശമില്ല.<br><span class="tag-adv">✓ മഴ പ്രതിരോധം:</span> മഴയിൽ നിന്ന് പൂർണ്ണ സംരക്ഷണം.</td>

                    <td><span class="tag-dis">✗ അധ്വാനം:</span> എല്ലാ തെങ്ങിലും കയറി കെട്ടേണ്ടതുണ്ട്.</td>

                  </tr>

                </tbody>

              </table>

            </div>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>5. ഗവേഷണ സ്ഥാപനം & സഹായം</span></h3>

            <p class="dossier-block-text">സാങ്കേതിക മാർഗ്ഗനിർദ്ദേശങ്ങൾക്ക് <strong>ICAR-സിപിസിആർഐ</strong> കാസർഗോഡ്, വിട്ടൽ കേന്ദ്രങ്ങളിലോ അടുത്തുള്ള കൃഷി ഭവനിലോ ബന്ധപ്പെടുക.</p>

          </div>

        </div>

      `,

      yld: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🔬</span><span>1. രോഗകാരണം (ഫൈറ്റോപ്ലാസ്മയും വാഹക കീടങ്ങളും)</span></h3>

            <p class="dossier-block-text">മഞ്ഞളിപ്പ് രോഗം (YLD) അടക്കയുടെ ഫ്ലോയം കോശങ്ങളിൽ വസിക്കുന്ന <strong>ഫൈറ്റോപ്ലാസ്മ</strong> എന്ന സൂക്ഷ്മാണു മൂലമുണ്ടാകുന്നു.</p>

            <ul class="dossier-bullets">

              <li><strong>വാഹക കീടങ്ങൾ:</strong> സസ്യ പേനുകൾ (<em>Proutista moesta</em>) വഴിയാണ് രോഗം പകരുന്നത്.</li>

              <li><strong>കാരണങ്ങൾ:</strong> മണ്ണിലെ അസിഡിറ്റി (കുറഞ്ഞ pH), നീർവാർച്ചയില്ലായ്മ, പൊട്ടാഷ്/മഗ്നീഷ്യം കുറവ്.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚠️</span><span>2. ലക്ഷണങ്ങളും വിളനാശവും</span></h3>

            <ul class="dossier-bullets">

              <li><strong>ഓല മഞ്ഞളിക്കൽ:</strong> താഴ്ഭാഗത്തെ ഓലകളുടെ അറ്റത്ത് നിന്ന് മഞ്ഞനിറം പടരുന്നു.</li>

              <li><strong>മണ്ട ചെറുതാകൽ:</strong> ഓലകൾ കുറുകുകയും മണ്ടയുടെ വലിപ്പം കുറയുകയും ചെയ്യുന്നു.</li>

              <li><strong>അടക്കയുടെ ഗുണനിലവാരം:</strong> അടക്ക ചെറുതാവുകയും പരിപ്പ് കറുത്ത് സ്പോഞ്ച് പോലെയാവുകയും ചെയ്യുന്നു.</li>

              <li><strong>വിളനഷ്ടം:</strong> 3-5 വർഷത്തിനുള്ളിൽ വിളവ് <strong>60% മുതൽ 80% വരെ</strong> കുറയുന്നു.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. സംരക്ഷണ മാർഗ്ഗങ്ങൾ (ICAR-CPCRI)</span></h3>

            <ul class="dossier-bullets">

              <li><strong>സന്തുലിത വളപ്രയോഗം (NPK):</strong> തെങ്ങൊന്നിന് പ്രതിവർഷം 100 ഗ്രാം നൈട്രജൻ, 40 ഗ്രാം ഫോസ്ഫറസ്, 140 ഗ്രാം പൊട്ടാഷ് എന്നിവ രണ്ട് തവണകളായി നൽകുക.</li>

              <li><strong>ജൈവവളം:</strong> തെങ്ങൊന്നിന് 12 കിലോഗ്രാം കാലിവളവും 12 കിലോഗ്രാം പച്ചിലവളവും നൽകുക.</li>

              <li><strong>നീർവാർച്ച:</strong> തോട്ടത്തിൽ വെള്ളക്കെട്ട് ഒഴിവാക്കാൻ ചാലുകൾ കീറുക.</li>

              <li><strong>ഇടവിളകൾ:</strong> കൊക്കോ, വാഴ തുടങ്ങിയ ഇടവിളകൾ കൃഷി ചെയ്യുക.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>4. ഗവേഷണ സ്ഥാപനം</span></h3>

            <p class="dossier-block-text">വിശദവിവരങ്ങൾക്ക് <strong>ICAR-സിപിസിആർഐ</strong> കാസർഗോഡുമായി ബന്ധപ്പെടുക.</p>

          </div>

        </div>

      `,

      healthy_nut: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🌰</span><span>1. ആരോഗ്യമുള്ള അടക്കയുടെ ഗുണമേന്മ മാനദണ്ഡങ്ങൾ</span></h3>

            <p class="dossier-block-text">ആരോഗ്യമുള്ള അടക്ക നല്ല പരിചരണത്തിന്റെ തെളിവാണ്: നല്ല ഞെട്ട് ബലം, മിനുസമുള്ള തൊലി, കട്ടിയുള്ള പരിപ്പ്.</p>

            <ul class="dossier-bullets">

              <li><strong>തൊലിയുടെ ഗുണമേന്മ:</strong> തിളക്കമുള്ള പച്ചയോ കടുത്ത ഓറഞ്ചോ നിറം, കുമിൾ പാടുകളില്ല.</li>

              <li><strong>ഞെട്ടിന്റെ ബലം:</strong> കുലയിൽ അടക്കകൾ ഉറച്ചുനിൽക്കുന്നു.</li>

              <li><strong>പരിപ്പിന്റെ സാന്ദ്രത:</strong> നല്ല ഘടനയും ഭാരവുമുള്ള പരിപ്പ്.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>📈</span><span>2. വളർച്ചയുടെ 4 ഘട്ടങ്ങൾ</span></h3>

            <ul class="dossier-bullets">

              <li><strong>ബട്ടൺ സ്റ്റേജ് (1-2 മാസം):</strong> പരാഗണത്തിന് ശേഷമുള്ള ഘട്ടം. കൊഴിച്ചിൽ ഒഴിവാക്കാൻ ബോറോൺ നൽകുക.</li>

              <li><strong>ഇളനീർ അടക്ക (3-5 മാസം):</strong> അടക്ക വളരുന്ന ഘട്ടം. മഹാലി തടയാൻ മരുന്ന് തളിക്കുക.</li>

              <li><strong>മൂത്ത അടക്ക (6-7 മാസം):</strong> പരിപ്പ് ഉറയ്ക്കുന്ന ഘട്ടം.</li>

              <li><strong>വിളവെഴുപ്പ് ഘട്ടം (8-9 മാസം):</strong> ഓറഞ്ച് നിറമാകുമ്പോൾ വിളവെടുക്കാം.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🛡️</span><span>3. ഉൽപ്പാദന വർദ്ധനവ് (ICAR-CPCRI)</span></h3>

            <ul class="dossier-bullets">

              <li><strong>സന്തുലിത വളം:</strong> 100 ഗ്രാം N, 40 ഗ്രാം P, 140 ഗ്രാം K.</li>

              <li><strong>സൂക്ഷ്മമൂലകങ്ങൾ:</strong> ബോറാക്സ് (12-15 ഗ്രാം), സിങ്ക് സൾഫേറ്റ് (20-25 ഗ്രാം).</li>

              <li><strong>വേനൽക്കാല നന:</strong> 4-6 ദിവസത്തിലൊരിക്കൽ 175-200 ലിറ്റർ വെള്ളം നൽകുക.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>4. സ്ഥാപനം</span></h3>

            <p class="dossier-block-text">മാനദണ്ഡങ്ങൾ <strong>BIS: 2228-1996</strong> പ്രകാരം നിശ്ചയിച്ചിരിക്കുന്നു. വിശദവിവരങ്ങൾക്ക് ICAR-CPCRI ബന്ധപ്പെടുക.</p>

          </div>

        </div>

      `,

      healthy_leaf: `

        <div class="dossier-sections-grid">

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🍃</span><span>1. ആരോഗ്യമുള്ള ഓലകളുടെ ഗുണമേന്മ</span></h3>

            <p class="dossier-block-text">ഓലകളാണ് തെങ്ങിന്റെ ഭക്ഷണ ഫാക്ടറി. ഇവയാണ് വിളവും ആയുസ്സും നിശ്ചയിക്കുന്നത്.</p>

            <ul class="dossier-bullets">

              <li><strong>ഓലകളുടെ എണ്ണം:</strong> ഒരു നല്ല തെങ്ങിൽ <strong>9 മുതൽ 12 വരെ പച്ച ഓലകൾ</strong> ഉണ്ടായിരിക്കണം.</li>

              <li><strong>പച്ചപ്പ്:</strong> മഞ്ഞളിപ്പില്ലാത്ത തിളക്കമുള്ള പച്ച നിറം.</li>

              <li><strong>കുരുത്തോല:</strong> നിവർന്നുനിൽക്കുന്ന ആരോഗ്യമുള്ള കുരുത്തോല.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>⚡</span><span>2. ധർമ്മങ്ങൾ</span></h3>

            <ul class="dossier-bullets">

              <li><strong>ഭക്ഷണ നിർമ്മാണം:</strong> ഓരോ ഓലയും 3-4 കുലകൾക്ക് ഭക്ഷണം നൽകുന്നു. 2 ഓലകൾ നഷ്ടപ്പെട്ടാൽ വിളവിൽ 15-25% കുറവുണ്ടാകാം.</li>

              <li><strong>പോഷക ആഗിരണം:</strong> വേരുകളിൽ നിന്ന് കാൽസ്യവും മഗ്നീഷ്യവും മുകളിലേക്ക് എത്തിക്കുന്നു.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🧪</span><span>3. പോഷകക്കുറവുകൾ</span></h3>

            <ul class="dossier-bullets">

              <li><strong>നൈട്രജൻ കുറവ്:</strong> ഓലകൾ മഞ്ഞളിക്കൽ. <em>പരിഹാരം:</em> യൂറിയ + ജൈവവളം നൽകുക.</li>

              <li><strong>പൊട്ടാഷ് കുറവ്:</strong> ഓലകളുടെ അറ്റം കരിയൽ. <em>പരിഹാരം:</em> MOP നൽകുക, പുതയിടുക.</li>

              <li><strong>മഗ്നീഷ്യം കുറവ്:</strong> ഓലകളിൽ മഞ്ഞ-ഓറഞ്ച് വരകൾ. <em>പരിഹാരം:</em> ഡോളമൈറ്റ് ചേർക്കുക.</li>

            </ul>

          </div>

          <div class="dossier-block">

            <h3 class="dossier-block-title"><span>🏛️</span><span>4. സ്ഥാപനം</span></h3>

            <p class="dossier-block-text">വിശദവിവരങ്ങൾക്ക് <strong>ICAR-സിപിസിആർഐ</strong> കാസർഗോഡുമായി ബന്ധപ്പെടുക.</p>

          </div>

        </div>

      `

    }

  };



  function updateDossierContent(lang) {

    const data = DOSSIER_I18N[lang] || DOSSIER_I18N['en'];

    if (!data) return;

    ['mahali', 'yld', 'healthy_nut', 'healthy_leaf'].forEach(cls => {

      const el = document.getElementById(`dossier-panel-${cls}`);

      if (el && data[cls]) {

        el.innerHTML = data[cls];

      }

    });

  }



  // Language State Management

  let currentLang = localStorage.getItem('arecalens_lang') || 'en';

  if (!I18N_STRINGS[currentLang]) currentLang = 'en';



  async function ensureLanguageLoaded(lang, langName) {

    if (!I18N_STRINGS[lang]) {

      I18N_STRINGS[lang] = { ...I18N_STRINGS.en };

    }

    try {

      const resp = await fetch('/api/translate/', {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify({

          target_lang: lang,

          lang_name: langName || lang,

          keys: I18N_STRINGS.en

        })

      });

      const data = await resp.json();

      if (data.success && data.translations) {

        I18N_STRINGS[lang] = { ...I18N_STRINGS[lang], ...data.translations };

        applyLanguage(lang);

      }

    } catch (e) {

      console.warn('Dynamic Gemini translation fetch notice:', e);

    }

  }



  function applyLanguage(lang) {

    if (!I18N_STRINGS[lang]) return;

    currentLang = lang;

    localStorage.setItem('arecalens_lang', lang);



    const strings = I18N_STRINGS[lang];



    // 1. Text translations

    document.querySelectorAll('[data-i18n]').forEach(el => {

      const key = el.getAttribute('data-i18n');

      if (strings[key]) {

        el.textContent = strings[key];

      }

    });



    // 2. HTML translations (if any)

    document.querySelectorAll('[data-i18n-html]').forEach(el => {

      const key = el.getAttribute('data-i18n-html');

      if (strings[key]) {

        el.innerHTML = strings[key];

      }

    });



    // 3. Header Active Language Label

    const headerActive = document.getElementById('header-active-lang');

    if (headerActive) headerActive.textContent = strings.lang_name;



    // 4. Update language selection cards in modal & book

    document.querySelectorAll('.lang-card-option').forEach(card => {

      if (card.getAttribute('data-lang') === lang) {

        card.classList.add('selected');

      } else {

        card.classList.remove('selected');

      }

    });



    // 5. Update continue button in modal

    const continueBtn = document.getElementById('confirm-lang-btn');

    if (continueBtn) {

      continueBtn.textContent = strings.btn_continue || 'Continue ➔';

    }



    // 6. Translate Main Result Disease Title (if present on Page 4)

    const resultDiseaseTitle = document.querySelector('.result-main-disease');

    if (resultDiseaseTitle) {

      const origText = resultDiseaseTitle.textContent.trim();

      resultDiseaseTitle.textContent = translateDiseaseName(origText, lang);

    }



    // 6b. Translate About page classification cards

    document.querySelectorAll('.cls-name-transizable').forEach(el => {

      const orig = el.getAttribute('data-orig-title') || el.textContent.trim();

      if (!el.getAttribute('data-orig-title')) el.setAttribute('data-orig-title', orig);

      el.textContent = translateDiseaseName(orig, lang);

    });



    // 7. Translate Model Probability Rows

    document.querySelectorAll('.class-prob-row').forEach(row => {

      const titleSpan = row.querySelector('.class-prob-header > span:first-child');

      if (titleSpan) {

        const hasTag = titleSpan.querySelector('.predicted-tag');

        const text = titleSpan.childNodes[0].textContent.trim();

        const translated = translateDiseaseName(text, lang);

        if (hasTag) {

          const tagText = strings.primary_match || 'PRIMARY MATCH';

          titleSpan.innerHTML = `${translated} <span class="predicted-tag" data-i18n="primary_match">${tagText}</span>`;

        } else {

          titleSpan.textContent = translated;

        }

      }

    });



    // 8. Translate Understanding Result Bullets

    const bulletsUl = document.querySelector('.understanding-bullets');

    if (bulletsUl) {

      const mainTitle = document.querySelector('.result-main-disease')?.textContent || '';

      const clsKey = getDiseaseKeyFromName(mainTitle);

      const bulletsList = (UNDERSTANDING_BULLETS_I18N[lang] && UNDERSTANDING_BULLETS_I18N[lang][clsKey])

        || UNDERSTANDING_BULLETS_I18N['en'][clsKey];

      if (bulletsList && bulletsList.length > 0) {

        bulletsUl.innerHTML = bulletsList.map(b => `<li>${b}</li>`).join('');

      }

    }



    // 9. Update Page 5 Disease Dossier Panels

    updateDossierContent(lang);



    // 10. Update Sound feedback button text

    updateSoundUI();



    // 11. Re-render scan history cards if grid exists

    renderHistoryGrid();

  }



  window.setLanguage = applyLanguage;

  applyLanguage(currentLang);





  // =========================================================================

  // 2. Language Selection Modal Interaction (Reference Video Frame 00:02)

  // =========================================================================

  const langModalBackdrop = document.getElementById('language-modal-backdrop');

  const openLangModalBtn = document.getElementById('open-lang-modal-btn');

  const confirmLangBtn = document.getElementById('confirm-lang-btn');

  let tempSelectedLang = currentLang;



  function openLanguageModal() {

    tempSelectedLang = currentLang;

    applyLanguage(currentLang);

    if (langModalBackdrop) langModalBackdrop.classList.add('open');

  }



  if (openLangModalBtn) openLangModalBtn.addEventListener('click', openLanguageModal);

  const heroLangTrigger = document.getElementById('hero-lang-switch-trigger');
  if (heroLangTrigger) {
    heroLangTrigger.addEventListener('click', () => {
      const heroCard = document.getElementById('hero-split-card');
      if (heroCard) {
        heroCard.classList.add('show-lang');
      } else {
        openLanguageModal();
      }
    });
  }



  if (langModalBackdrop) {

    langModalBackdrop.addEventListener('click', (e) => {

      if (e.target === langModalBackdrop) {

        langModalBackdrop.classList.remove('open');

      }

    });

  }



  // Language selection handling for both modal and book page

  document.querySelectorAll('.lang-card-option, .lang-book-card').forEach(card => {

    card.addEventListener('click', async () => {

      tempSelectedLang = card.getAttribute('data-lang');

      const langName = card.getAttribute('data-lang-name') || tempSelectedLang;

      document.querySelectorAll('.lang-card-option, .lang-book-card').forEach(c => c.classList.remove('selected'));

      document.querySelectorAll(`[data-lang="${tempSelectedLang}"]`).forEach(c => c.classList.add('selected'));

      playSoundCue('click');

      

      // If language strings aren't fully loaded, fetch them from Gemini/cache

      if (!I18N_STRINGS[tempSelectedLang] || Object.keys(I18N_STRINGS[tempSelectedLang]).length < 50) {

        await ensureLanguageLoaded(tempSelectedLang, langName);

      }

      applyLanguage(tempSelectedLang);

    });

  });



  if (confirmLangBtn && langModalBackdrop) {

    confirmLangBtn.addEventListener('click', () => {

      applyLanguage(tempSelectedLang);

      langModalBackdrop.classList.remove('open');

    });

  }



  // Custom Language Input Handler (Powered by Gemini)

  const applyCustomLangBtn = document.getElementById('apply-custom-lang-btn');

  const customLangInput = document.getElementById('custom-lang-input');

  if (applyCustomLangBtn && customLangInput) {

    applyCustomLangBtn.addEventListener('click', async () => {

      const customName = customLangInput.value.trim();

      if (!customName) return;

      const customCode = customName.toLowerCase().replace(/[^a-z]/g, '').slice(0, 8);

      applyCustomLangBtn.textContent = 'Translating...';

      await ensureLanguageLoaded(customCode, customName);

      applyLanguage(customCode);

      applyCustomLangBtn.textContent = 'Translate ➔';

      if (langModalBackdrop) langModalBackdrop.classList.remove('open');

    });

  }



  // Gemini API Key Save Handler

  const saveGeminiKeyBtn = document.getElementById('save-gemini-key-btn');

  const geminiKeyInput = document.getElementById('gemini-key-input');

  const geminiKeyFeedback = document.getElementById('gemini-key-feedback');

  const geminiKeyBadge = document.getElementById('gemini-key-badge');

  if (saveGeminiKeyBtn && geminiKeyInput) {

    saveGeminiKeyBtn.addEventListener('click', async () => {

      const keyVal = geminiKeyInput.value.trim();

      if (!keyVal) return;

      try {

        saveGeminiKeyBtn.textContent = 'Saving...';

        const resp = await fetch('/api/save-key/', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({ api_key: keyVal })

        });

        const data = await resp.json();

        if (data.success) {

          geminiKeyInput.value = '';

          geminiKeyFeedback.textContent = '✓ Gemini API key securely saved to .env!';

          geminiKeyFeedback.style.display = 'block';

          geminiKeyFeedback.style.color = '#16a34a';

          if (geminiKeyBadge) {

            geminiKeyBadge.textContent = 'Active / Saved';

            geminiKeyBadge.style.background = '#dcfce7';

          }

        } else {

          geminiKeyFeedback.textContent = 'Error: ' + (data.error || 'Could not save key');

          geminiKeyFeedback.style.display = 'block';

          geminiKeyFeedback.style.color = '#dc2626';

        }

      } catch (e) {

        geminiKeyFeedback.textContent = 'Network error saving key';

        geminiKeyFeedback.style.display = 'block';

      } finally {

        saveGeminiKeyBtn.textContent = 'Save Key';

      }

    });

  }



  // 3. BOOK ARCHITECTURE & SLIDE DECK TRANSITION CONTROLLER

  // =========================================================================

  let currentBookPage = 1;

  let isAnimatingSlide = false;



  function goToBookPage(pageNum, isInstant = false) {

    const targetPage = document.getElementById(`book-page-${pageNum}`);

    if (!targetPage) return;



    if (pageNum === currentBookPage && targetPage.classList.contains('active')) {

      return;

    }



    const prevPageNum = currentBookPage;

    currentBookPage = pageNum;

    const isForward = pageNum > prevPageNum;



    // Update universal stepper indicators

    const stepItems = document.querySelectorAll('.book-step-item');

    stepItems.forEach(item => {

      const step = parseInt(item.getAttribute('data-step') || '1', 10);

      item.classList.remove('active', 'completed');

      const numElem = item.querySelector('.book-step-num');



      if (step < pageNum) {

        item.classList.add('completed');

        if (numElem) numElem.textContent = '✓';

      } else if (step === pageNum) {

        item.classList.add('active');

        if (numElem) numElem.textContent = step;

      } else {

        if (numElem) numElem.textContent = step;

      }

    });



    const currentPage = document.getElementById(`book-page-${prevPageNum}`);



    if (isInstant || !currentPage || currentPage === targetPage) {

      document.querySelectorAll('.book-page').forEach(p => {

        p.className = 'book-page';

      });

      targetPage.className = 'book-page active';

      window.scrollTo({ top: 0, behavior: 'smooth' });

      return;

    }



    // Smooth horizontal slide deck animation

    isAnimatingSlide = true;



    // Clear animations on other pages

    document.querySelectorAll('.book-page').forEach(p => {

      if (p !== currentPage && p !== targetPage) {

        p.className = 'book-page';

      }

    });



    if (isForward) {

      currentPage.className = 'book-page active slide-out-left';

      targetPage.className = 'book-page active slide-in-right';

    } else {

      currentPage.className = 'book-page active slide-out-right';

      targetPage.className = 'book-page active slide-in-left';

    }



    playSoundCue('click');

    window.scrollTo({ top: 0, behavior: 'smooth' });



    setTimeout(() => {

      currentPage.className = 'book-page';

      targetPage.className = 'book-page active';

      isAnimatingSlide = false;

    }, 480);

  }



  // Bind Stepper Click Navigation

  document.querySelectorAll('.book-step-item').forEach(item => {

    item.addEventListener('click', function () {

      if (isAnimatingSlide) return;

      const step = parseInt(this.getAttribute('data-step') || '1', 10);

      goToBookPage(step);

    });

  });



  // Slide 1 (Welcome & Start) Navigation Buttons

  const coverStartBtn = document.getElementById('cover-start-btn');
  const heroSplitCard = document.getElementById('hero-split-card');
  const langBackIntroBtn = document.getElementById('lang-back-intro-btn');
  const langContinueStepBtn = document.getElementById('lang-continue-step-btn');

  const coverDossierBtn = document.getElementById('cover-dossier-btn');

  if (coverStartBtn) {

    coverStartBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      if (heroSplitCard) {
        playSoundCue('click');
        heroSplitCard.classList.add('show-lang');
      } else {
        goToBookPage(2);
      }

    });

  }

  if (coverDossierBtn) {

    coverDossierBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(5); // Slide into Disease Dossier

    });

  }



  // Slide 2 (Specimen Input) Navigation Buttons

  if (langBackIntroBtn) {
    langBackIntroBtn.addEventListener('click', () => {
      if (heroSplitCard) {
        playSoundCue('click');
        heroSplitCard.classList.remove('show-lang');
      }
    });
  }

  if (langContinueStepBtn) {
    langContinueStepBtn.addEventListener('click', () => {
      if (isAnimatingSlide) return;
      playSoundCue('success');
      goToBookPage(2);
    });
  }

  const inputPrevBtn = document.getElementById('input-prev-btn');

  const inputNextBtn = document.getElementById('input-next-btn');

  if (inputPrevBtn) {

    inputPrevBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(1); // Slide back to Welcome

    });

  }



  function startAnalysisPipeline() {

    const inputEl = document.getElementById('image-upload-input');

    if (!inputEl || !inputEl.files || inputEl.files.length === 0) {

      // Auto-load instant specimen sample if user clicked without picking

      generateSampleSpecimen('healthy_nut');

    }



    // Mirror Specimen Thumbnail into Slide 3 Neural HUD Viewfinder

    const previewImgEl = document.getElementById('preview-image-elem');

    const hudThumbEl = document.getElementById('hud-specimen-thumb');

    if (previewImgEl && hudThumbEl && previewImgEl.src && previewImgEl.src !== '#') {

      hudThumbEl.src = previewImgEl.src;

    }



    // Slide smoothly into Slide 3 (Neural HUD)

    goToBookPage(3);



    // Execute background AJAX ResNet-50 inference + phased HUD animation

    executeNeuralPipelineAJAX();

  }



  if (inputNextBtn) {

    inputNextBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      startAnalysisPipeline();

    });

  }



  // Slide 3 Phased Neural Screening HUD Simulation + Parallel Background AJAX

  function executeNeuralPipelineAJAX() {

    const progressBar = document.getElementById('hud-progress-bar');

    const odometerEl = document.getElementById('hud-percentage-counter');

    const phaseRows = [

      document.getElementById('phase-row-1'),

      document.getElementById('phase-row-2'),

      document.getElementById('phase-row-3'),

      document.getElementById('phase-row-4')

    ];

    const statusTitle = document.getElementById('hud-status-title');

    const statusSub = document.getElementById('hud-status-sub');

    const form = document.getElementById('disease-upload-form');



    // Smooth Odometer Counter Animation

    function animateOdometer(startVal, endVal, durationMs) {

      if (!odometerEl) return;

      const startTime = performance.now();

      function step(now) {

        const elapsed = now - startTime;

        const p = Math.min(elapsed / durationMs, 1);

        const ease = 1 - Math.pow(1 - p, 3);

        const currentVal = Math.round(startVal + (endVal - startVal) * ease);

        odometerEl.textContent = currentVal;

        if (p < 1) requestAnimationFrame(step);

      }

      requestAnimationFrame(step);

    }



    // Reset HUD timeline

    if (odometerEl) odometerEl.textContent = '0';

    phaseRows.forEach((r, idx) => {

      if (r) {

        r.className = (idx === 0) ? 'hud-phase-row active' : 'hud-phase-row';

        const dot = r.querySelector('.phase-dot');

        if (dot) dot.textContent = (idx + 1);

      }

    });



    // Milestone 1: Ingestion & Tensor Normalization (0 - 450ms)

    if (progressBar) progressBar.style.width = '25%';

    animateOdometer(0, 25, 420);

    if (statusTitle) statusTitle.textContent = 'Ingesting Specimen & Normalizing RGB Tensor...';

    if (statusSub) statusSub.textContent = 'Resizing to 224x224 and applying ImageNet normalization.';



    // Construct FormData from the upload form

    const formData = new FormData(form);



    // Track AJAX fetch promise and HUD visual timer concurrently

    const ajaxPromise = fetch(form.action || window.location.href, {

      method: 'POST',

      body: formData

    }).then(res => {

      if (!res.ok) throw new Error(`HTTP Error ${res.status}`);

      return res.text();

    });



    // Milestone 2: Feature Extraction (450ms - 950ms)

    setTimeout(() => {

      if (progressBar) progressBar.style.width = '55%';

      animateOdometer(25, 55, 480);

      if (phaseRows[0]) {

        phaseRows[0].className = 'hud-phase-row done';

        const dot0 = phaseRows[0].querySelector('.phase-dot');

        if (dot0) dot0.textContent = '✓';

      }

      if (phaseRows[1]) phaseRows[1].className = 'hud-phase-row active';

      if (statusTitle) statusTitle.textContent = 'Extracting 50 Residual Convolutional Blocks...';

      if (statusSub) statusSub.textContent = 'Aggregating 2048-dimensional feature vectors across bottleneck layers.';

    }, 450);



    // Milestone 3: Grad-CAM Backpropagation (950ms - 1450ms)

    setTimeout(() => {

      if (progressBar) progressBar.style.width = '85%';

      animateOdometer(55, 85, 480);

      if (phaseRows[1]) {

        phaseRows[1].className = 'hud-phase-row done';

        const dot1 = phaseRows[1].querySelector('.phase-dot');

        if (dot1) dot1.textContent = '✓';

      }

      if (phaseRows[2]) phaseRows[2].className = 'hud-phase-row active';

      if (statusTitle) statusTitle.textContent = 'Backpropagating Grad-CAM Layer4 Attention...';

      if (statusSub) statusSub.textContent = 'Computing activation gradients to construct Explainable AI heatmaps.';

    }, 950);



    // Milestone 4: Agronomic Advisory (1450ms - 1750ms)

    setTimeout(() => {

      if (progressBar) progressBar.style.width = '100%';

      animateOdometer(85, 100, 300);

      if (phaseRows[2]) {

        phaseRows[2].className = 'hud-phase-row done';

        const dot2 = phaseRows[2].querySelector('.phase-dot');

        if (dot2) dot2.textContent = '✓';

      }

      if (phaseRows[3]) {

        phaseRows[3].className = 'hud-phase-row done';

        const dot3 = phaseRows[3].querySelector('.phase-dot');

        if (dot3) dot3.textContent = '✓';

      }

      if (statusTitle) statusTitle.textContent = 'Diagnosis & Explainable AI Complete!';

      if (statusSub) statusSub.textContent = 'Transitioning to diagnostic report and visual evidence...';

      playSoundCue('success');

    }, 1450);



    // Minimum visual HUD duration (1750ms) so user perceives the neural scanner

    const minDelayPromise = new Promise(resolve => setTimeout(resolve, 1750));



    Promise.all([ajaxPromise, minDelayPromise])

      .then(([htmlText]) => {

        const parser = new DOMParser();

        const doc = parser.parseFromString(htmlText, 'text/html');



        // Extract result section from the returned result.html

        const parsedResultSection = doc.getElementById('book-page-4');

        const dynamicContainer = document.getElementById('results-dynamic-stage');



        if (parsedResultSection && dynamicContainer) {

          const resultsGrid = parsedResultSection.querySelector('.results-dashboard-grid');

          const noticeCard = parsedResultSection.querySelector('.card');



          dynamicContainer.innerHTML = '';

          if (noticeCard && resultsGrid) {

            dynamicContainer.appendChild(noticeCard.cloneNode(true));

            dynamicContainer.appendChild(resultsGrid.cloneNode(true));

          } else {

            dynamicContainer.innerHTML = parsedResultSection.innerHTML;

          }



          // Show footer on results page

          const navFooter = document.getElementById('result-nav-footer');

          if (navFooter) navFooter.style.display = 'flex';



          // Extract scan data for history tracking

          const scanDataElem = doc.getElementById('scan-result-data');

          if (scanDataElem) {

            recordScanToHistory(scanDataElem);

          }



          // Apply active language to newly injected results HTML

          applyLanguage(currentLang);



          // Initialize interactive controls for the freshly injected results

          initResultsStudio(dynamicContainer);



          // Smoothly trigger the animation of moving to the next slide (Results)!

          goToBookPage(4);

        } else {

          // Fallback in case of unexpected structure: submit normally

          form.submit();

        }

      })

      .catch(err => {

        console.error('Inference error:', err);

        form.submit();

      });

  }



  // Slide 4 Result Navigation Buttons

  const resultFreshBtn = document.getElementById('result-fresh-btn');

  const resultToDossierBtn = document.getElementById('result-to-dossier-btn');

  const dossierToResultBtn = document.getElementById('dossier-to-result-btn');



  if (resultFreshBtn) {

    resultFreshBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(2); // Slide back to specimen input

    });

  }

  if (resultToDossierBtn) {

    resultToDossierBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(5); // Slide forward to disease dossier

    });

  }

  if (dossierToResultBtn) {

    dossierToResultBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(4); // Slide back to results

    });

  }



  // Slide 5 Dossier Navigation Buttons

  const dossierPrevBtn = document.getElementById('dossier-prev-btn');

  const dossierStartBtn = document.getElementById('dossier-start-btn');

  if (dossierPrevBtn) {

    dossierPrevBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(2);

    });

  }

  if (dossierStartBtn) {

    dossierStartBtn.addEventListener('click', () => {

      if (isAnimatingSlide) return;

      goToBookPage(1);

    });

  }



  // Disease Dossier Tabs Switching

  document.querySelectorAll('.dossier-tab-btn').forEach(btn => {

    btn.addEventListener('click', function () {

      const targetClass = this.getAttribute('data-dossier-class');

      document.querySelectorAll('.dossier-tab-btn').forEach(b => b.classList.remove('active'));

      this.classList.add('active');



      document.querySelectorAll('.dossier-content-panel').forEach(panel => {

        panel.classList.remove('active');

      });

      const activePanel = document.getElementById(`dossier-panel-${targetClass}`);

      if (activePanel) activePanel.classList.add('active');

      playSoundCue('click');

    });

  });



  // Top Nav Brand Links

  const brandHomeLink = document.getElementById('brand-home-link');

  if (brandHomeLink) {

    brandHomeLink.addEventListener('click', (e) => {
      if (document.getElementById('book-page-1')) {
        goToBookPage(1);
      } else {
        window.location.href = '/';
      }
    });

  }

  const navAnalyze = document.getElementById('nav-analyze');

  const navGuide = document.getElementById('nav-guide');

  const navHistory = document.getElementById('nav-history');
  const methLaunchBtn = document.getElementById('meth-launch-screening-btn');
  const methGuideBtn = document.getElementById('meth-explore-guide-btn');
  if (methLaunchBtn) {
    methLaunchBtn.addEventListener('click', () => {
      goToBookPage(2);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  if (methGuideBtn) {
    methGuideBtn.addEventListener('click', () => {
      goToBookPage(5);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  if (navAnalyze) {

    navAnalyze.addEventListener('click', (e) => {
      if (document.getElementById('book-page-2')) {
        e.preventDefault();
        goToBookPage(2);
      }
    });

  }

  if (navGuide) {

    navGuide.addEventListener('click', (e) => {
      if (document.getElementById('book-page-5')) {
        e.preventDefault();
        goToBookPage(5);
      } else {
        window.location.href = '/?step=5';
      }
    });

  }

  if (navHistory) {

    navHistory.addEventListener('click', () => {

      openHistoryModal();

    });

  }



  // STARTING PAGE INITIALIZATION:

  // If on result.html (book-page-4 exists and has server-rendered results), show Page 4.

  // If on home page, ALWAYS start at Page 1 (Welcome) on every refresh!

  if (window.location.pathname.includes('/result/') || (document.getElementById('book-page-4') && !document.getElementById('results-dynamic-stage'))) {

    goToBookPage(4, true);

  } else {

    if (document.getElementById('book-page-1')) {
      const urlParams = new URLSearchParams(window.location.search);
      const stepParam = parseInt(urlParams.get('step') || '1', 10);
      goToBookPage(stepParam, true);
    }

  }



  // =========================================================================

  // 5. File Upload, Drag-and-Drop & Preview (Reference Video Frame 00:05, 01:13)

  // =========================================================================

  const dropzone = document.getElementById('upload-dropzone');

  const fileInput = document.getElementById('image-upload-input');

  const previewCard = document.getElementById('preview-card-wrap');

  const previewImg = document.getElementById('preview-image-elem');

  const previewName = document.getElementById('preview-filename-text');

  const removePreviewBtn = document.getElementById('remove-preview-btn');

  const changePhotoLink = document.getElementById('change-photo-link');

  const submitBtn = document.getElementById('submit-analyze-btn');

  const uploadForm = document.getElementById('disease-upload-form');



  if (dropzone && fileInput) {

    ['dragenter', 'dragover'].forEach(name => {

      dropzone.addEventListener(name, (e) => {

        e.preventDefault();

        e.stopPropagation();

        dropzone.classList.add('dragover');

      });

    });



    ['dragleave', 'drop'].forEach(name => {

      dropzone.addEventListener(name, (e) => {

        e.preventDefault();

        e.stopPropagation();

        dropzone.classList.remove('dragover');

      });

    });



    dropzone.addEventListener('drop', (e) => {

      const dt = e.dataTransfer;

      if (dt && dt.files && dt.files.length > 0) {

        fileInput.files = dt.files;

        handleFile(dt.files[0]);

      }

    });



    fileInput.addEventListener('change', function () {

      if (this.files && this.files.length > 0) {

        handleFile(this.files[0]);

      }

    });



    if (changePhotoLink) {

      changePhotoLink.addEventListener('click', () => fileInput.click());

    }



    if (removePreviewBtn) {

      removePreviewBtn.addEventListener('click', () => {

        fileInput.value = '';

        if (previewCard) previewCard.style.display = 'none';

        if (dropzone) dropzone.style.display = 'flex';

      });

    }

  }



  function handleFile(file) {

    const allowed = ['image/jpeg', 'image/png', 'image/jpg'];

    const maxBytes = 10 * 1024 * 1024; // 10MB



    if (!allowed.includes(file.type.toLowerCase()) && !file.name.match(/\.(jpg|jpeg|png)$/i)) {

      alert('Unsupported file format. Please upload a JPG, JPEG, or PNG image.');

      fileInput.value = '';

      return;

    }



    if (file.size > maxBytes) {

      alert(`File size is ${(file.size / (1024*1024)).toFixed(1)} MB. Maximum allowed size is 10 MB.`);

      fileInput.value = '';

      return;

    }



    const reader = new FileReader();

    reader.onload = function (e) {

      if (previewImg) previewImg.src = e.target.result;

      if (previewName) {

        const sizeKb = (file.size / 1024).toFixed(1);

        previewName.textContent = `${file.name} (${sizeKb} kB)`;

      }

      if (dropzone) dropzone.style.display = 'none';

      if (previewCard) previewCard.style.display = 'block';

    };

    reader.readAsDataURL(file);

  }



  // Trigger File Input from Dropzone Action Button

  const triggerFileSelect = document.getElementById('trigger-file-select');

  if (triggerFileSelect && fileInput) {

    triggerFileSelect.addEventListener('click', (e) => {

      e.preventDefault();

      e.stopPropagation();

      playSoundCue('click');

      fileInput.click();

    });

  }



  // Trigger Camera Studio from Hero & Dropzone Buttons

  const triggerCameraModal = document.getElementById('trigger-camera-modal');

  const heroCameraLaunchBtn = document.getElementById('hero-camera-launch-btn');

  [triggerCameraModal, heroCameraLaunchBtn].forEach(btn => {

    if (btn) {

      btn.addEventListener('click', (e) => {

        e.preventDefault();

        e.stopPropagation();

        openCameraStudio();

      });

    }

  });



  // Instant Specimen Quick-Tester Generator

  function generateSampleSpecimen(sampleType) {

    const canvas = document.createElement('canvas');

    canvas.width = 400;

    canvas.height = 400;

    const ctx = canvas.getContext('2d');



    if (sampleType === 'healthy_leaf') {

      // Lush green arecanut palm leaflet

      ctx.fillStyle = '#1e3d2f';

      ctx.fillRect(0, 0, 400, 400);



      const grad = ctx.createLinearGradient(100, 0, 300, 400);

      grad.addColorStop(0, '#2d6a4f');

      grad.addColorStop(0.5, '#40916c');

      grad.addColorStop(1, '#1b4332');

      ctx.fillStyle = grad;

      ctx.beginPath();

      ctx.moveTo(200, 30);

      ctx.quadraticCurveTo(340, 160, 240, 370);

      ctx.quadraticCurveTo(200, 390, 160, 370);

      ctx.quadraticCurveTo(60, 160, 200, 30);

      ctx.fill();



      // Central pale midrib

      ctx.strokeStyle = '#95d5b2';

      ctx.lineWidth = 4;

      ctx.beginPath();

      ctx.moveTo(200, 30);

      ctx.lineTo(200, 380);

      ctx.stroke();



      // Parallel side veins

      ctx.strokeStyle = 'rgba(183, 228, 199, 0.45)';

      ctx.lineWidth = 1.5;

      for (let y = 60; y < 360; y += 18) {

        ctx.beginPath();

        ctx.moveTo(200, y);

        ctx.lineTo(130, y + 25);

        ctx.moveTo(200, y);

        ctx.lineTo(270, y + 25);

        ctx.stroke();

      }

    } else if (sampleType === 'healthy_nut') {

      // Golden-orange arecanut cluster

      ctx.fillStyle = '#232b26';

      ctx.fillRect(0, 0, 400, 400);



      const nuts = [

        { cx: 160, cy: 170, r: 55, c1: '#f4a261', c2: '#e76f51' },

        { cx: 240, cy: 170, r: 55, c1: '#e9c46a', c2: '#f4a261' },

        { cx: 200, cy: 235, r: 60, c1: '#f4a261', c2: '#d48b28' },

        { cx: 145, cy: 250, r: 45, c1: '#e9c46a', c2: '#e09f3e' },

        { cx: 255, cy: 250, r: 45, c1: '#e09f3e', c2: '#b26d18' }

      ];

      nuts.forEach(n => {

        const g = ctx.createRadialGradient(n.cx - 15, n.cy - 15, 10, n.cx, n.cy, n.r);

        g.addColorStop(0, n.c1);

        g.addColorStop(1, n.c2);

        ctx.fillStyle = g;

        ctx.beginPath();

        ctx.arc(n.cx, n.cy, n.r, 0, Math.PI * 2);

        ctx.fill();

        ctx.strokeStyle = '#8d5b1b';

        ctx.lineWidth = 2;

        ctx.stroke();

      });

    } else if (sampleType === 'mahali') {

      // Mahali fruit rot: water soaked dark rotting nut with fungal patches

      ctx.fillStyle = '#1c1b18';

      ctx.fillRect(0, 0, 400, 400);



      const g = ctx.createRadialGradient(180, 180, 20, 200, 200, 100);

      g.addColorStop(0, '#5a3d28');

      g.addColorStop(0.6, '#382315');

      g.addColorStop(1, '#1f130b');

      ctx.fillStyle = g;

      ctx.beginPath();

      ctx.arc(200, 200, 95, 0, Math.PI * 2);

      ctx.fill();



      // Dark necrotic rot patches

      ctx.fillStyle = '#211107';

      for (let i = 0; i < 7; i++) {

        ctx.beginPath();

        ctx.arc(160 + (i * 15) % 70, 160 + (i * 20) % 70, 25 + (i * 5) % 15, 0, Math.PI * 2);

        ctx.fill();

      }



      // Whitish fungal mycelium patches

      ctx.fillStyle = 'rgba(235, 240, 235, 0.75)';

      for (let i = 0; i < 28; i++) {

        ctx.beginPath();

        ctx.arc(150 + Math.sin(i) * 42, 180 + Math.cos(i) * 42, 3 + (i % 4), 0, Math.PI * 2);

        ctx.fill();

      }

    } else if (sampleType === 'yld') {

      // Yellow leaf disease: intense chlorosis and tip scorch

      ctx.fillStyle = '#1e3d2f';

      ctx.fillRect(0, 0, 400, 400);



      const grad = ctx.createLinearGradient(100, 0, 300, 400);

      grad.addColorStop(0, '#d4a373');

      grad.addColorStop(0.3, '#e9c46a');

      grad.addColorStop(0.7, '#e76f51');

      grad.addColorStop(1, '#582f0e');

      ctx.fillStyle = grad;

      ctx.beginPath();

      ctx.moveTo(200, 30);

      ctx.quadraticCurveTo(340, 160, 240, 370);

      ctx.quadraticCurveTo(200, 390, 160, 370);

      ctx.quadraticCurveTo(60, 160, 200, 30);

      ctx.fill();



      // Scorched necrotic brown margin

      ctx.strokeStyle = '#4a2810';

      ctx.lineWidth = 7;

      ctx.stroke();



      // Necrotic tip

      ctx.fillStyle = '#3a1e05';

      ctx.beginPath();

      ctx.moveTo(200, 30);

      ctx.lineTo(225, 75);

      ctx.lineTo(175, 75);

      ctx.closePath();

      ctx.fill();

    }



    try {

      const dataUrl = canvas.toDataURL('image/jpeg', 0.92);

      const filename = `sample_${sampleType}.jpg`;

      const sampleFile = dataURLtoFile(dataUrl, filename);



      if (fileInput) {

        const dt = new DataTransfer();

        dt.items.add(sampleFile);

        fileInput.files = dt.files;

        handleFile(sampleFile);

        playSoundCue('success');



        const hudThumbEl = document.getElementById('hud-specimen-thumb');

        if (hudThumbEl) hudThumbEl.src = dataUrl;

      }

    } catch (err) {

      console.warn('Sample generation error:', err);

    }

  }



  function dataURLtoFile(dataurl, filename) {

    const arr = dataurl.split(',');

    const mime = arr[0].match(/:(.*?);/)[1];

    const bstr = atob(arr[1]);

    let n = bstr.length;

    const u8arr = new Uint8Array(n);

    while (n--) {

      u8arr[n] = bstr.charCodeAt(n);

    }

    return new File([u8arr], filename, { type: mime });

  }



  document.querySelectorAll('.specimen-sample-btn').forEach(btn => {

    btn.addEventListener('click', function (e) {

      e.preventDefault();

      const sample = this.getAttribute('data-sample');

      generateSampleSpecimen(sample);

    });

  });



  // Submit Button & Pipeline Trigger

  if (uploadForm) {

    uploadForm.addEventListener('submit', function (e) {

      e.preventDefault();

      startAnalysisPipeline();

    });

  }



  // =========================================================================

  // 6. Web Audio API Tactile Sound Feedback Synthesizer Controls

  // =========================================================================

  const soundToggleBtn = document.getElementById('sound-toggle-btn');

  updateSoundUI();



  if (soundToggleBtn) {

    soundToggleBtn.addEventListener('click', () => {

      isSoundEnabled = !isSoundEnabled;

      localStorage.setItem('arecalens_sound', isSoundEnabled ? 'enabled' : 'muted');

      updateSoundUI();

      if (isSoundEnabled) playSoundCue('click');

    });

  }



  // Attach subtle click feedback to interactive controls

  document.querySelectorAll('.nav-item-btn, .lang-selector-btn, .guide-tab-btn, .cam-tab-btn, .filter-chip').forEach(el => {

    el.addEventListener('click', () => playSoundCue('click'));

  });



  // =========================================================================

  // 7. Live Specimen Camera Studio (Webcam Stream & Capture)

  // =========================================================================

  const cameraToggleCheck = document.getElementById('camera-toggle-check');

  const cameraModal = document.getElementById('camera-modal-backdrop');

  const cameraCloseBtn = document.getElementById('camera-modal-close-btn');

  const cameraVideo = document.getElementById('camera-video-stream');

  const cameraCanvas = document.getElementById('camera-capture-canvas');

  const cameraShutterBtn = document.getElementById('camera-shutter-btn');

  let activeMediaStream = null;



  async function openCameraStudio() {

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {

      alert('Camera access is not supported by this browser. Please upload a photo file.');

      if (cameraToggleCheck) cameraToggleCheck.checked = false;

      return;

    }



    try {

      activeMediaStream = await navigator.mediaDevices.getUserMedia({

        video: {

          facingMode: { ideal: 'environment' },

          width: { ideal: 1280 },

          height: { ideal: 720 }

        },

        audio: false

      });



      if (cameraVideo) {

        cameraVideo.srcObject = activeMediaStream;

        cameraVideo.play();

      }



      if (cameraModal) cameraModal.classList.add('open');

      playSoundCue('click');

    } catch (err) {

      console.warn('Camera stream error:', err);

      alert('Could not access your camera. Please check browser permissions or upload an image.');

      if (cameraToggleCheck) cameraToggleCheck.checked = false;

    }

  }



  function closeCameraStudio() {

    if (activeMediaStream) {

      activeMediaStream.getTracks().forEach(track => track.stop());

      activeMediaStream = null;

    }

    if (cameraVideo) cameraVideo.srcObject = null;

    if (cameraModal) cameraModal.classList.remove('open');

    if (cameraToggleCheck) cameraToggleCheck.checked = false;

  }



  if (cameraToggleCheck) {

    cameraToggleCheck.addEventListener('change', function () {

      if (this.checked) {

        openCameraStudio();

      } else {

        closeCameraStudio();

      }

    });

  }



  if (cameraCloseBtn) cameraCloseBtn.addEventListener('click', closeCameraStudio);



  if (cameraModal) {

    cameraModal.addEventListener('click', (e) => {

      if (e.target === cameraModal) closeCameraStudio();

    });

  }



  if (cameraShutterBtn && cameraVideo && cameraCanvas) {

    cameraShutterBtn.addEventListener('click', () => {

      playSoundCue('shutter');

      const w = cameraVideo.videoWidth || 640;

      const h = cameraVideo.videoHeight || 480;

      cameraCanvas.width = w;

      cameraCanvas.height = h;



      const ctx = cameraCanvas.getContext('2d');

      ctx.drawImage(cameraVideo, 0, 0, w, h);



      cameraCanvas.toBlob((blob) => {

        if (!blob) return;

        const capturedFile = new File([blob], `specimen_camera_${Date.now()}.jpg`, { type: 'image/jpeg' });



        if (fileInput) {

          const dt = new DataTransfer();

          dt.items.add(capturedFile);

          fileInput.files = dt.files;

          handleFile(capturedFile);

        }



        closeCameraStudio();

      }, 'image/jpeg', 0.95);

    });

  }



  // =========================================================================

  // 8. Diagnostic Results Interactive Controls (Dynamic & Static Studio)

  // =========================================================================

  function initResultsStudio(scope = document) {

    const camStage = scope.querySelector('#cam-display-stage') || document.getElementById('cam-display-stage');

    const curtainStage = scope.querySelector('#curtain-slider-stage') || document.getElementById('curtain-slider-stage');

    const curtainOverlayWrap = scope.querySelector('#curtain-overlay-wrap') || document.getElementById('curtain-overlay-wrap');

    const curtainDividerLine = scope.querySelector('#curtain-divider-line') || document.getElementById('curtain-divider-line');

    const baseImgLayer = scope.querySelector('#cam-base-layer') || document.getElementById('cam-base-layer');

    const overlayImgLayer = scope.querySelector('#cam-overlay-layer') || document.getElementById('cam-overlay-layer');

    const opacitySlider = scope.querySelector('#overlay-opacity-slider') || document.getElementById('overlay-opacity-slider');

    const opacityText = scope.querySelector('#opacity-val-text') || document.getElementById('opacity-val-text');

    const opacityContainer = scope.querySelector('#opacity-slider-container') || document.getElementById('opacity-slider-container');

    const camButtons = scope.querySelectorAll('.cam-tab-btn');

    const compareLabels = scope.querySelectorAll('.cam-compare-label');



    if (opacitySlider && overlayImgLayer) {

      opacitySlider.oninput = function () {

        const val = this.value;

        if (opacityText) opacityText.textContent = `${val}%`;

        overlayImgLayer.style.opacity = val / 100;

      };

    }



    camButtons.forEach(btn => {

      btn.onclick = function () {

        const mode = this.getAttribute('data-mode');

        camButtons.forEach(b => b.classList.remove('active'));

        this.classList.add('active');



        if (mode === 'curtain') {

          if (camStage) camStage.style.display = 'none';

          if (curtainStage) curtainStage.style.display = 'block';

          if (opacityContainer) opacityContainer.style.display = 'none';

          triggerCurtainPeekAnimation();

          return;

        }



        if (curtainStage) curtainStage.style.display = 'none';



        if (mode === 'input') {

          if (camStage) {

            camStage.style.display = 'flex';

            camStage.classList.remove('compare-mode');

          }

          if (compareLabels) compareLabels.forEach(l => l.style.display = 'none');

          if (baseImgLayer) baseImgLayer.style.display = 'block';

          if (overlayImgLayer) overlayImgLayer.style.display = 'none';

          if (opacityContainer) opacityContainer.style.display = 'none';

        } else if (mode === 'overlay') {

          if (camStage) {

            camStage.style.display = 'flex';

            camStage.classList.remove('compare-mode');

          }

          if (compareLabels) compareLabels.forEach(l => l.style.display = 'none');

          if (baseImgLayer) baseImgLayer.style.display = 'block';

          if (overlayImgLayer) {

            overlayImgLayer.style.display = 'block';

            if (opacitySlider) overlayImgLayer.style.opacity = opacitySlider.value / 100;

          }

          if (opacityContainer) opacityContainer.style.display = 'flex';

        } else if (mode === 'compare') {

          if (camStage) {

            camStage.style.display = 'grid';

            camStage.classList.add('compare-mode');

          }

          if (compareLabels) compareLabels.forEach(l => l.style.display = 'block');

          if (baseImgLayer) baseImgLayer.style.display = 'block';

          if (overlayImgLayer) {

            overlayImgLayer.style.display = 'block';

            overlayImgLayer.style.opacity = '1';

          }

          if (opacityContainer) opacityContainer.style.display = 'none';

        }

      };

    });



    if (curtainStage && curtainOverlayWrap && curtainDividerLine) {

      let isDraggingCurtain = false;



      function setCurtainPosition(clientX) {

        const rect = curtainStage.getBoundingClientRect();

        let offsetX = clientX - rect.left;

        let pct = (offsetX / rect.width) * 100;

        pct = Math.max(2, Math.min(98, pct));



        curtainOverlayWrap.style.clipPath = `polygon(0 0, ${pct}% 0, ${pct}% 100%, 0 100%)`;

        curtainDividerLine.style.left = `${pct}%`;

      }



      curtainStage.onmousedown = (e) => {

        isDraggingCurtain = true;

        setCurtainPosition(e.clientX);

      };



      window.onmousemove = (e) => {

        if (isDraggingCurtain) setCurtainPosition(e.clientX);

      };



      window.onmouseup = () => {

        isDraggingCurtain = false;

      };



      curtainStage.ontouchstart = (e) => {

        if (e.touches.length > 0) {

          isDraggingCurtain = true;

          setCurtainPosition(e.touches[0].clientX);

        }

      };



      window.ontouchmove = (e) => {

        if (isDraggingCurtain && e.touches.length > 0) {

          setCurtainPosition(e.touches[0].clientX);

        }

      };



      window.ontouchend = () => {

        isDraggingCurtain = false;

      };

    }



    // Staggered Spring-Loaded Probability Bars Animation

    const probBars = scope.querySelectorAll('.class-prob-bar-fill');

    probBars.forEach((bar, idx) => {

      const targetWidth = bar.getAttribute('data-target-width') || bar.style.width;

      bar.setAttribute('data-target-width', targetWidth);

      bar.style.width = '0%';

      setTimeout(() => {

        bar.style.transition = 'width 0.95s cubic-bezier(0.16, 1, 0.3, 1)';

        bar.style.width = targetWidth;

      }, 100 + idx * 110);

    });



    // Auto Peek Curtain Glance Animation

    function triggerCurtainPeekAnimation() {

      if (!curtainOverlayWrap || !curtainDividerLine) return;

      let startTime = performance.now();

      const duration = 1200;

      function peek(now) {

        const elapsed = now - startTime;

        const progress = Math.min(elapsed / duration, 1);

        const offset = Math.sin(progress * Math.PI) * -14;

        const pct = 50 + offset;

        curtainOverlayWrap.style.clipPath = `polygon(0 0, ${pct}% 0, ${pct}% 100%, 0 100%)`;

        curtainDividerLine.style.left = `${pct}%`;

        if (progress < 1) requestAnimationFrame(peek);

      }

      setTimeout(() => requestAnimationFrame(peek), 280);

    }



    // Gauge Counter Animation

    const gaugeValCircle = scope.querySelector('.gauge-val') || document.querySelector('.gauge-val');

    const gaugeText = scope.querySelector('.gauge-text') || document.querySelector('.gauge-text');

    if (gaugeValCircle && gaugeText) {

      const targetPct = parseFloat(gaugeValCircle.getAttribute('data-percentage') || 0);

      const radius = (gaugeValCircle.r && gaugeValCircle.r.baseVal) ? gaugeValCircle.r.baseVal.value : 38;

      const circumference = 2 * Math.PI * radius;

      gaugeValCircle.style.strokeDasharray = `${circumference} ${circumference}`;

      gaugeValCircle.style.strokeDashoffset = circumference;



      const finalOffset = circumference - (targetPct / 100) * circumference;

      const duration = 1200;

      const startTime = performance.now();



      function animateGauge(currentTime) {

        const elapsed = currentTime - startTime;

        const progress = Math.min(elapsed / duration, 1);

        const ease = 1 - Math.pow(1 - progress, 3);

        const currentPct = (targetPct * ease).toFixed(1);

        gaugeText.textContent = `${currentPct}%`;

        const currentOffset = circumference - (ease * (circumference - finalOffset));

        gaugeValCircle.style.strokeDashoffset = currentOffset;



        if (progress < 1) {

          requestAnimationFrame(animateGauge);

        } else {

          gaugeText.textContent = `${targetPct}%`;

          gaugeValCircle.style.strokeDashoffset = finalOffset;

          playSoundCue('success');

        }

      }



      setTimeout(() => {

        requestAnimationFrame(animateGauge);

      }, 200);

    }



    // Accordion Toggle for Model Scores

    const toggleScoresBtn = scope.querySelector('#toggle-scores-btn') || document.getElementById('toggle-scores-btn');

    const allScoresPanel = scope.querySelector('#all-scores-panel') || document.getElementById('all-scores-panel');

    if (toggleScoresBtn && allScoresPanel) {

      toggleScoresBtn.onclick = () => {

        const isOpen = allScoresPanel.classList.toggle('open');

        toggleScoresBtn.innerHTML = isOpen 

          ? `<span data-i18n="see_all_scores">▴ Hide four model scores</span>`

          : `<span data-i18n="see_all_scores">▾ See all four model scores</span>`;

      };

    }



    // Print Diagnostic Report

    const printReportBtn = scope.querySelector('#print-report-btn') || document.getElementById('print-report-btn');

    if (printReportBtn) {

      printReportBtn.onclick = () => {

        playSoundCue('click');

        window.print();

      };

    }



    // Copy Advisory

    const copyAdvisoryBtn = scope.querySelector('#copy-advisory-btn') || document.getElementById('copy-advisory-btn');

    const copyAdvisoryText = scope.querySelector('#copy-advisory-text') || document.getElementById('copy-advisory-text');

    if (copyAdvisoryBtn) {

      copyAdvisoryBtn.onclick = () => {

        const disease = (scope.querySelector('.result-main-disease') || document.querySelector('.result-main-disease'))?.textContent.trim() || 'Arecanut Specimen';

        const score = (scope.querySelector('.gauge-text') || document.querySelector('.gauge-text'))?.textContent.trim() || 'N/A';

        const bullets = Array.from((scope.querySelectorAll('.understanding-bullets li') || document.querySelectorAll('.understanding-bullets li')))

          .map(li => `• ${li.textContent.trim()}`)

          .join('\n');



        const textToCopy = `ARECALENS PHYTOSANITARY DIAGNOSTIC SUMMARY\n` +

          `Specimen Diagnosis: ${disease}\n` +

          `Relative Model Score: ${score}\n` +

          `Timestamp: ${new Date().toLocaleString()}\n\n` +

          `Key Insights & Recommended Care:\n${bullets}\n\n` +

          `Note: Local AI screening reference only. Confirm critical symptoms with ICAR-CPCRI or local agricultural extension officer.`;



        navigator.clipboard.writeText(textToCopy).then(() => {

          playSoundCue('click');

          if (copyAdvisoryText) copyAdvisoryText.textContent = '✓ Copied!';

          setTimeout(() => {

            if (copyAdvisoryText) copyAdvisoryText.textContent = 'Copy Advisory';

          }, 2200);

        }).catch(err => {

          console.warn('Clipboard write failed:', err);

        });

      };

    }

  }



  // Initialize Results Studio for any static content present on load

  initResultsStudio();



  // =========================================================================

  // 11. Disease Guide Search & Filter Engine

  // =========================================================================

  const guideSearchInput = document.getElementById('guide-search-input');

  const filterChips = document.querySelectorAll('.filter-chip');



  if (guideSearchInput) {

    guideSearchInput.addEventListener('input', function () {

      const query = this.value.toLowerCase().trim();

      document.querySelectorAll('.guide-detail-sheet').forEach(sheet => {

        if (!query) {

          // Restore default view based on active tab

          const activeBtn = document.querySelector('.guide-tab-btn.active');

          const activeClass = activeBtn ? activeBtn.getAttribute('data-class') : 'healthy_leaf';

          sheet.style.display = (sheet.getAttribute('data-class') === activeClass) ? 'block' : 'none';

          return;

        }



        const textContent = sheet.textContent.toLowerCase();

        if (textContent.includes(query)) {

          sheet.style.display = 'block';

        } else {

          sheet.style.display = 'none';

        }

      });

    });

  }



  filterChips.forEach(chip => {

    chip.addEventListener('click', function () {

      filterChips.forEach(c => c.classList.remove('active'));

      this.classList.add('active');



      const filter = this.getAttribute('data-filter');

      if (filter === 'all') {

        showGuideView('healthy_leaf');

      } else if (filter === 'foliar') {

        showGuideView('yld');

      } else if (filter === 'fruit') {

        showGuideView('mahali');

      } else if (filter === 'healthy') {

        showGuideView('healthy_leaf');

      }

    });

  });



  // =========================================================================

  // 12. Scan History Tracking (Client-side LocalStorage) (Reference Video Frame 00:44)

  // =========================================================================

  function recordScanToHistory(resultDataContainer) {

    if (!resultDataContainer) return;

    try {

      const scanItem = {

        id: Date.now(),

        image: resultDataContainer.dataset.imageThumb || '',

        disease: resultDataContainer.dataset.disease || 'Unknown',

        confidence: resultDataContainer.dataset.confidence || '0%',

        filename: resultDataContainer.dataset.filename || 'Specimen',

        timestamp: new Date().toLocaleString()

      };



      let history = JSON.parse(localStorage.getItem('arecalens_history') || '[]');

      history.unshift(scanItem);

      if (history.length > 8) history = history.slice(0, 8);

      localStorage.setItem('arecalens_history', JSON.stringify(history));

      renderHistoryGrid();

    } catch (err) {

      console.warn('Could not record history in localStorage:', err);

    }

  }



  const resultDataContainer = document.getElementById('scan-result-data');

  if (resultDataContainer) {

    recordScanToHistory(resultDataContainer);

  }



  // =========================================================================

  // Scan History Modal & Client-Side LocalStorage Engine

  // =========================================================================

  function openHistoryModal() {

    renderHistoryGrid();

    const modal = document.getElementById('history-modal-backdrop');

    if (modal) {

      modal.classList.add('open');

      playSoundCue('click');

    }

  }



  function closeHistoryModal() {

    const modal = document.getElementById('history-modal-backdrop');

    if (modal) {

      modal.classList.remove('open');

      playSoundCue('click');

    }

  }



  const historyCloseBtn = document.getElementById('history-modal-close-btn');

  if (historyCloseBtn) {

    historyCloseBtn.addEventListener('click', closeHistoryModal);

  }



  const historyModal = document.getElementById('history-modal-backdrop');

  if (historyModal) {

    historyModal.addEventListener('click', (e) => {

      if (e.target === historyModal) {

        closeHistoryModal();

      }

    });

  }



  document.addEventListener('keydown', (e) => {

    if (e.key === 'Escape') {

      const modal = document.getElementById('history-modal-backdrop');

      if (modal && modal.classList.contains('open')) {

        closeHistoryModal();

      }

    }

  });



  function renderHistoryGrid() {

    const grid = document.getElementById('history-cards-grid');

    const emptyState = document.getElementById('empty-history-state');

    if (!grid) return;



    let history = [];

    try {

      history = JSON.parse(localStorage.getItem('arecalens_history') || '[]');

    } catch (e) {

      history = [];

    }

    grid.innerHTML = '';



    if (history.length === 0) {

      if (emptyState) emptyState.style.display = 'block';

      return;

    }



    if (emptyState) emptyState.style.display = 'none';



    const fallbackSvg = "data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='76' height='76' viewBox='0 0 24 24' fill='none' stroke='%232d6a4f' stroke-width='2'%3E%3Cpath d='M12 2L12 22'/%3E%3Cpath d='M12 7C8 7 4 9 4 13C4 17 8 19 12 19'/%3E%3Cpath d='M12 7C16 7 20 9 20 13C20 17 16 19 12 19'/%3E%3C/svg%3E";



    const strings = I18N_STRINGS[currentLang] || I18N_STRINGS['en'];

    history.forEach(item => {

      const card = document.createElement('div');

      card.className = 'history-card';

      const isHealthy = item.disease && item.disease.toLowerCase().includes('healthy');

      const tagText = isHealthy ? (strings.history_tag_healthy || 'HEALTHY CONTROL') : (strings.history_tag_diseased || 'DISEASE PATTERN SUSPECTED');

      const tagColor = isHealthy ? 'color:#15803d;' : 'color:#b91c1c;';

      const scoreLabel = strings.history_score_label || 'Relative score:';

      const localizedDisease = translateDiseaseName(item.disease, currentLang);



      const thumbImg = document.createElement('img');

      thumbImg.className = 'history-thumb';

      thumbImg.alt = localizedDisease || 'Specimen';

      thumbImg.src = (item.image && item.image.length > 20) ? item.image : fallbackSvg;

      thumbImg.onerror = function () {

        this.onerror = null;

        this.src = fallbackSvg;

      };



      const infoWrap = document.createElement('div');

      infoWrap.className = 'history-info';

      infoWrap.innerHTML = `

        <div>

          <div class="history-tag" style="${tagColor}">${tagText}</div>

          <div class="history-disease" title="${localizedDisease}">${localizedDisease}</div>

          <div class="history-time">${item.filename} • ${item.timestamp}</div>

        </div>

        <div style="font-size:0.78rem; font-weight:700; color:var(--c-forest-green); margin-top:0.4rem; display: flex; align-items: center; gap: 0.35rem;">

          <span>${scoreLabel}</span>

          <span style="background: #e8f5ec; padding: 0.1rem 0.45rem; border-radius: 6px;">${item.confidence}</span>

        </div>

      `;



      card.appendChild(thumbImg);

      card.appendChild(infoWrap);

      grid.appendChild(card);

    });

  }



  const clearHistoryBtn = document.getElementById('clear-history-btn');

  if (clearHistoryBtn) {

    clearHistoryBtn.addEventListener('click', () => {

      localStorage.removeItem('arecalens_history');

      playSoundCue('click');

      renderHistoryGrid();

    });

  }

});

