import streamlit as st
from PIL import Image
import tempfile
import os
from google import genai
from gtts import gTTS
import base64

# Initialize Gemini
client = genai.Client(api_key="AIzaSyATt_TjsSwJUyVXYy5RnEonF-nEUq00t9g")

# Streamlit App Config
st.set_page_config(page_title="🌿 AI Agriculture Advisor", layout="wide")

# Custom CSS for Beautiful UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Raleway', sans-serif;
        background-image: url('https://images.unsplash.com/photo-1549887534-5bdfc1a4ef4e?auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-attachment: fixed;
    }

    .main-title {
        font-size: 48px;
        color: #2e7d32;
        text-align: center;
        margin-top: 30px;
        text-shadow: 1px 1px 3px #c5e1a5;
    }

    .subtitle {
        font-size: 20px;
        color: #33691e;
        text-align: center;
        margin-bottom: 30px;
    }

    .section-box {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
    }

    .result-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-left: 5px solid #66bb6a;
        border-radius: 12px;
        font-size: 1.1em;
        color: #2e7d32;
    }

    .audio-box {
        background-color: #f1f8e9;
        padding: 15px;
        border-radius: 12px;
        margin-top: 20px;
    }

    .stTabs [role="tab"] {
        font-size: 1.1em;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px 10px 0 0;
        background: #aed581;
        color: white;
    }

    .stButton > button {
        background-color: #66bb6a !important;
        color: white !important;
        font-size: 16px;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-title'>🌱 AI Agriculture Advisor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Diagnose your crops and get voice-based expert advice using AI</div>", unsafe_allow_html=True)

# Language Selection
lang_option = st.selectbox("🌐 Choose Language", ["English", "Telugu", "Hindi"])
lang_code = {"English": "en", "Telugu": "te", "Hindi": "hi"}[lang_option]

# Tabs
tab1, tab2 = st.tabs(["📸 Diagnose with Image", "🔊 Voice Output"])

# TAB 1: Image Diagnosis
with tab1:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📄 Upload Image (Crop / Leaf / Soil)")
    uploaded_img = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"])

    if uploaded_img:
        st.image(uploaded_img, caption="🌿 Uploaded Image", use_column_width=True)
        with st.spinner("🧠 Gemini analyzing your image..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img_path = tmp.name
                img = Image.open(uploaded_img)
                img.save(img_path)

            uploaded_file = client.files.upload(file=img_path)

            prompt = f"""
            You are an agricultural expert. Analyze the uploaded image of a crop, leaf, or soil and provide:
            1. Crop identification
            2. Disease/pest/nutrient deficiency symptoms
            3. Recommended treatments (organic & chemical)
            4. Prevention & yield tips
            Reply in {lang_option}.
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[uploaded_file, prompt]
            )

        st.success("✅ Analysis Complete!")
        st.subheader("🌾 AI Suggestion")
        st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)

        # Save for Voice Output
        st.session_state['gemini_response'] = response.text
        st.session_state['selected_lang_code'] = lang_code

    st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: Voice Output
with tab2:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🔊 Hear Gemini's Advice")

    if 'gemini_response' in st.session_state:
        text_to_speak = st.session_state['gemini_response']
        lang = st.session_state['selected_lang_code']

        with st.spinner("🔊 Generating audio..."):
            tts = gTTS(text=text_to_speak, lang=lang)
            audio_path = os.path.join(tempfile.gettempdir(), "gemini_audio.mp3")
            tts.save(audio_path)

            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                <div class='audio-box'>
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.info("📸 Upload an image in the first tab to hear AI advice.")
    st.markdown("</div>", unsafe_allow_html=True)

# Additional AI Services Section
st.markdown("### 🌟 Additional Smart Farming Tools")

with st.expander("📘 Agriculture Assistance (Ask Any Question)"):
    user_query = st.text_input("🤔 Ask your farming-related question (e.g., irrigation, seeds, pests)")
    if user_query:
        with st.spinner("💬 Gemini preparing answer..."):
            prompt = f"""
            You are an expert agriculture assistant. Answer the following question in {lang_option}:
            {user_query}
            Keep the response simple, actionable, and farmer-friendly.
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt]
            )
            st.success("✅ Answer Ready:")
            st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)

with st.expander("🧪 Soil Health Analysis"):
    st.markdown("Enter soil parameters to get AI analysis:")
    nitrogen = st.number_input("Nitrogen (N)", 0.0, 1000.0, step=1.0)
    phosphorus = st.number_input("Phosphorus (P)", 0.0, 1000.0, step=1.0)
    potassium = st.number_input("Potassium (K)", 0.0, 1000.0, step=1.0)
    ph = st.number_input("Soil pH", 0.0, 14.0, value=7.0, step=0.1)
    moisture = st.number_input("Moisture (%)", 0.0, 100.0, step=0.5)

    if st.button("🔍 Analyze Soil"):
        soil_prompt = f"""
        Analyze the following soil health values and give a detailed report in {lang_option}:
        Nitrogen: {nitrogen}, Phosphorus: {phosphorus}, Potassium: {potassium}, pH: {ph}, Moisture: {moisture}.
        Include nutrient deficiency signs, suitable crops, and improvement suggestions.
        """
        with st.spinner("🧠 Gemini analyzing soil..."):
            soil_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[soil_prompt]
            )
            st.success("✅ Soil Report:")
            st.markdown(f"<div class='result-box'>{soil_response.text}</div>", unsafe_allow_html=True)

with st.expander("🌱 Smart Fertilizer Recommendation"):
    crop = st.text_input("🌾 Enter Crop Name (e.g., Rice, Wheat, Tomato)")
    stage = st.selectbox("🌿 Crop Stage", ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"])
    if st.button("🧠 Recommend Fertilizer"):
        fert_prompt = f"""
        Suggest fertilizers for {crop} crop in {stage} stage.
        Provide both organic and chemical options. Include dosage and timing.
        Reply in {lang_option}.
        """
        with st.spinner("🧪 Gemini generating recommendations..."):
            fert_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[fert_prompt]
            )
            st.success("✅ Fertilizer Suggestions:")
            st.markdown(f"<div class='result-box'>{fert_response.text}</div>", unsafe_allow_html=True)
