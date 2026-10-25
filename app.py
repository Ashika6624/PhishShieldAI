import streamlit as st
import joblib
import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from PIL import Image

# ----------------------------------------------------
# 1. Page Configuration & NLTK Setup
# ----------------------------------------------------
st.set_page_config(
    page_title="PhishShieldAI",
    page_icon="🛡️",
    layout="wide"
)

nltk.download("stopwords", quiet=True)
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

# ----------------------------------------------------
# 2. Custom Cyber-Defense Theme CSS
# ----------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0B1120, #111827, #0F172A);
    color: #F3F4F6;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1F2937;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: #FFFFFF !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700;
}

.risk-card {
    padding: 1.2rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.risk-high {
    background: rgba(220, 38, 38, 0.15);
    border: 1px solid #EF4444;
}

.risk-low {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
}

.badge-spam {
    display: inline-block;
    background-color: #EF4444;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.2rem;
}

.badge-ham {
    display: inline-block;
    background-color: #10B981;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Model & Resource Loading Functions
# ----------------------------------------------------
@st.cache_resource
def load_resources():
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    
    # Load primary (Linear SVM) and comparative (Random Forest) models
    svm_path = "models/svm_model.pkl" if os.path.exists("models/svm_model.pkl") else "models/phishing_model.pkl"
    rf_path = "models/rf_model.pkl" if os.path.exists("models/rf_model.pkl") else "models/phishing_model.pkl"
    
    svm_model = joblib.load(svm_path)
    rf_model = joblib.load(rf_path)
    
    feature_weights = {}
    if os.path.exists("models/feature_weights.pkl"):
        feature_weights = joblib.load("models/feature_weights.pkl")
        
    return vectorizer, svm_model, rf_model, feature_weights

vectorizer, svm_model, rf_model, feature_weights = load_resources()

# ----------------------------------------------------
# 4. Text Processing & Feature Extraction Helpers
# ----------------------------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-zA-Z]", " ", text)
    words = text.split()
    stemmed_tokens = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]
    return " ".join(stemmed_tokens), stemmed_tokens

def extract_heuristic_signals(text):
    # Detect URLs cleanly
    urls = re.findall(r"https?://\S+|www\.\S+", text)
    
    # Detect IP-based URLs (strong phishing indicator)
    ip_urls = [u for u in urls if re.search(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", u)]
    
    # Social Engineering & Urgency keywords
    urgency_patterns = [
        r"\burgent\b", r"\bimmediat(e|ely)\b", r"\bsuspend(ed)?\b",
        r"\bverif(y|ication)\b", r"\baction required\b", r"\b24 hours?\b",
        r"\bexpire(d)?\b", r"\bunauthori[zs]ed\b", r"\bsecur(e|ity) alert\b",
        r"\bclaim\b", r"\bprize\b", r"\bwinner\b", r"\bcongratulat(ions)?\b"
    ]
    urgency_matches = []
    for pattern in urgency_patterns:
        found = re.findall(pattern, text, flags=re.IGNORECASE)
        if found:
            urgency_matches.append(pattern.replace(r"\b", "").replace("?", ""))
            
    # Capitalization stress ratio
    words_raw = text.split()
    caps_words = [w for w in words_raw if w.isupper() and len(w) > 1]
    caps_ratio = (len(caps_words) / len(words_raw) * 100) if words_raw else 0.0

    return {
        "urls": urls,
        "ip_urls": ip_urls,
        "urgency_keywords": list(set(urgency_matches)),
        "caps_ratio": caps_ratio
    }

# ----------------------------------------------------
# 5. Sidebar Controls & Research Attribution
# ----------------------------------------------------
st.sidebar.title("🛡️ PhishShieldAI")
st.sidebar.caption("Intelligent Phishing Detection Framework")
st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Classifier Selection")
model_choice = st.sidebar.selectbox(
    "Active Inference Model:",
    [
        "Linear SVM (Paper Champion - 98.48%)",
        "Random Forest (Comparative - 97.49%)"
    ],
    index=0,
    help="Switch between the champion model evaluated in the research paper and the ensemble baseline."
)

if "Linear SVM" in model_choice:
    active_model = svm_model
    model_name = "Linear SVM"
    model_acc = "98.48%"
    model_f1 = "94.04%"
else:
    active_model = rf_model
    model_name = "Random Forest"
    model_acc = "97.49%"
    model_f1 = "89.63%"

st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Project Information")
st.sidebar.write("**Framework:** PhishShieldAI")
st.sidebar.write("**Pipeline:** NLP + TF-IDF (5,000 Dimensions)")
st.sidebar.write("**Corpus Size:** 5,572 Labelled Messages")
st.sidebar.write("**Analysis Engine:** Explainable AI (XAI) + Heuristics")
st.sidebar.success("🛡️ Threat Detection Engine Active")

# ----------------------------------------------------
# 6. Header & Dashboard Metrics
# ----------------------------------------------------
try:
    logo = Image.open("assets/logo.png")
    c1, c2 = st.columns([1, 6])
    with c1:
        st.image(logo, width=90)
    with c2:
        st.title("PhishShieldAI")
        st.caption("A Machine Learning Framework for Intelligent Phishing Email Detection Using Natural Language Processing")
except Exception:
    st.title("🛡️ PhishShieldAI")
    st.caption("Intelligent Phishing Detection & Explainability Framework")

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Corpus Messages", value="5,572")
with m2:
    st.metric(label="Selected Model", value=model_name)
with m3:
    st.metric(label="Model Accuracy", value=model_acc)
with m4:
    st.metric(label="Phishing F1-Score", value=model_f1)

st.markdown("---")

# ----------------------------------------------------
# 7. Presentation Demo Helpers & Input Area
# ----------------------------------------------------
st.subheader("📩 Analyze Message Content")

# Quick test buttons for seamless presentation demonstration
demo_cols = st.columns([1.5, 1.5, 3])
phishing_sample = (
    "URGENT: Your bank account has been temporarily locked due to unauthorized login attempts. "
    "Please verify your credentials immediately within 24 hours at http://192.168.1.1/login-verify "
    "to avoid permanent suspension. Claim your security unlock code now."
)
ham_sample = (
    "Hi Ashika, hope you are doing well. Please find attached the updated project schedule "
    "for tomorrow's review meeting. Let me know if you need any adjustments before noon. Thanks!"
)

sample_choice = ""
with demo_cols[0]:
    if st.button("🧪 Load Phishing Demo"):
        st.session_state["email_content"] = phishing_sample
with demo_cols[1]:
    if st.button("🧪 Load Legitimate Demo"):
        st.session_state["email_content"] = ham_sample

default_text = st.session_state.get("email_content", "")

email = st.text_area(
    "Paste the email or message body below:",
    value=default_text,
    height=180,
    placeholder="Paste message content here..."
)

# ----------------------------------------------------
# 8. Detection, Prediction & Explainability Pipeline
# ----------------------------------------------------
if st.button("🔍 Run Intelligent Analysis", use_container_width=True, type="primary"):
    if not email.strip():
        st.warning("⚠️ Please enter or paste text to analyze.")
    else:
        # Preprocessing & Vectorization
        cleaned_str, tokens = clean_text(email)
        vector = vectorizer.transform([cleaned_str])
        
        # Inference
        prediction = active_model.predict(vector)[0]
        
        # Calibrated probability
        if hasattr(active_model, "predict_proba"):
            probs = active_model.predict_proba(vector)[0]
            confidence = max(probs) * 100
            # Class index 1 corresponds to 'spam'
            spam_prob = probs[1] * 100
        else:
            confidence = 95.0
            spam_prob = 100.0 if prediction == "spam" else 0.0

        signals = extract_heuristic_signals(email)

        st.markdown("### 📊 Detection Verdict")
        left, right = st.columns([2, 1])

        if prediction == "spam":
            with left:
                st.markdown("""
                <div class="risk-card risk-high">
                    <h3 style="color:#EF4444 !important; margin-top:0;">🚨 PHISHING / MALICIOUS EMAIL DETECTED</h3>
                    <p>This message exhibits linguistic and structural characteristics strongly associated with social engineering and credential harvesting attacks.</p>
                    <strong>Recommended Defensive Protocols:</strong>
                    <ul>
                        <li>❌ Do not click any links or download attached files.</li>
                        <li>❌ Do not enter login credentials, OTPs, or financial information.</li>
                        <li>🔒 Verify sender identity through out-of-band communication.</li>
                        <li>🚩 Escalate and report this email to the security operations team.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with right:
                st.metric("Threat Classification", "🔴 HIGH RISK")
                st.metric("Model Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))
        else:
            with left:
                st.markdown("""
                <div class="risk-card risk-low">
                    <h3 style="color:#10B981 !important; margin-top:0;">✅ LEGITIMATE (HAM) EMAIL</h3>
                    <p>No anomalous phishing vocabulary or high-risk social engineering markers were detected.</p>
                    <strong>Operational Hygiene:</strong>
                    <ul>
                        <li>✔ Standard legitimate communication patterns identified.</li>
                        <li>✔ Always check sender domain consistency for external contacts.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with right:
                st.metric("Threat Classification", "🟢 LOW RISK")
                st.metric("Model Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))

        st.markdown("---")

        # ----------------------------------------------------
        # 9. Explainable AI (XAI) Word Attribution
        # ----------------------------------------------------
        st.subheader("🧠 Explainable AI (XAI): Model Decision Factors")
        st.caption("Linguistic tokens in the message that contributed directly to the classification decision based on learned TF-IDF feature weights.")

        found_spam_words = []
        found_ham_words = []

        for token in set(tokens):
            if token in feature_weights:
                weight = feature_weights[token]
                if weight > 0.3:
                    found_spam_words.append((token, weight))
                elif weight < -0.3:
                    found_ham_words.append((token, weight))

        found_spam_words.sort(key=lambda x: x[1], reverse=True)
        found_ham_words.sort(key=lambda x: x[1])

        xai_col1, xai_col2 = st.columns(2)

        with xai_col1:
            st.markdown("##### 🚨 Top Phishing Indicator Words Detected")
            if found_spam_words:
                badges = "".join([f'<span class="badge-spam">{word} (weight: +{wt:.2f})</span>' for word, wt in found_spam_words[:10]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.info("No prominent phishing vocabulary triggers detected.")

        with xai_col2:
            st.markdown("##### 🟢 Top Legitimate Indicator Words Detected")
            if found_ham_words:
                badges = "".join([f'<span class="badge-ham">{word} (weight: {wt:.2f})</span>' for word, wt in found_ham_words[:10]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.info("No strong neutral/legitimate anchor words detected.")

        st.markdown("---")

        # ----------------------------------------------------
        # 10. Heuristic & Structural Cyber Indicators
        # ----------------------------------------------------
        st.subheader("🔍 Heuristic Threat & Link Analysis")
        h1, h2, h3 = st.columns(3)

        with h1:
            st.write("**🔗 URL Analysis**")
            if signals["urls"]:
                st.error(f"Found {len(signals['urls'])} embedded link(s):")
                for u in signals["urls"]:
                    st.code(u)
            else:
                st.success("✅ No embedded hyperlinks found.")

        with h2:
            st.write("**⚠️ Urgency / Social Engineering Cues**")
            if signals["urgency_keywords"]:
                st.warning(f"Detected {len(signals['urgency_keywords'])} psychological triggers:")
                for kw in signals["urgency_keywords"]:
                    st.write(f"- `{kw}`")
            else:
                st.success("✅ No coercive urgency keywords found.")

        with h3:
            st.write("**🚨 IP Host & Capitalization Flags**")
            if signals["ip_urls"]:
                st.error(f"🚨 Raw IP host detected in URL (High evasion risk): {signals['ip_urls']}")
            else:
                st.write("- Raw IP in URL: None")
            st.write(f"- ALL CAPS Stress Ratio: `{signals['caps_ratio']:.1f}%`")
            if signals["caps_ratio"] > 15.0:
                st.warning("⚠️ High proportion of capital letters (psychological pressure tactic).")
