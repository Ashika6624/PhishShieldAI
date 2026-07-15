import streamlit as st
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from PIL import Image

# ----------------------------
# Download NLTK Data
# ----------------------------
nltk.download("stopwords", quiet=True)

# ----------------------------
# Load Model
# ----------------------------
model = joblib.load("models/phishing_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="PhishShieldAI",
    page_icon="🛡️",
    layout="wide"
)

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#0B1120,#111827,#0F172A);
}

section[data-testid="stSidebar"]{
background:#111827;
}

.block-container{
padding-top:2rem;
}

h1,h2,h3{
color:white;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("🛡️ PhishShieldAI")
st.sidebar.markdown("---")
st.sidebar.header("Project Information")
st.sidebar.write("🎓 MCA Mini Project")
st.sidebar.write("👩 Student : Ashika Poojary")
st.sidebar.write("🤖 Model : Random Forest")
st.sidebar.write("📊 Accuracy : 97.40%")
st.sidebar.write("📧 Dataset : SMS Spam Collection")
st.sidebar.success("AI Powered Email Security")

# ----------------------------
# Logo
# ----------------------------
try:
    logo = Image.open("assets/logo.png")
    c1,c2 = st.columns([1,5])

    with c1:
        st.image(logo,width=90)

    with c2:
        st.title("PhishShieldAI")
        st.caption("Hybrid Machine Learning Framework for Intelligent Phishing Email Detection")

except:
    st.title("🛡️ PhishShieldAI")

st.markdown("---")

# ----------------------------
# Dashboard
# ----------------------------
a, b, c, d = st.columns([1, 2, 1, 1])

with a:
    st.metric("Emails","5572")

with b:
    st.metric("Model","Random Forest")

with c:
    st.metric("Accuracy","97.40%")

with d:
    st.metric("Status","Secure")

st.markdown("---")

# ----------------------------
# Input
# ----------------------------
st.header("📩 Analyze Email")

email=st.text_area(
    "Paste email content below",
    height=250,
    key="email_box"
)

# ----------------------------
# Cleaning Function
# ----------------------------
def clean_text(text):

    text=text.lower()

    text=re.sub(r"http\\S+","",text)

    text=re.sub(r"[^a-zA-Z]"," ",text)

    words=text.split()

    words=[
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)

# ----------------------------
# Prediction
# ----------------------------
if st.button("🔍 Analyze Email",use_container_width=True):

    if email.strip()=="":

        st.warning("Please paste an email.")

    else:

        cleaned=clean_text(email)

        vector=vectorizer.transform([cleaned])

        prediction=model.predict(vector)[0]

        probability=model.predict_proba(vector)[0]

        confidence=max(probability)*100

        st.markdown("---")

        left,right=st.columns([2,1])
        if prediction == "spam":

            with left:

                st.error("🚨 PHISHING EMAIL DETECTED")

                st.markdown("""
## ⚠ Security Alert

This email appears to contain phishing or spam characteristics.

### Recommendations

- ❌ Do not click suspicious links
- ❌ Do not download unknown attachments
- ❌ Do not share passwords or OTPs
- ✅ Verify the sender before responding
- ✅ Report suspicious emails to your IT team
""")
                with right:
                    st.metric("Risk Level", "🔴 HIGH")
                st.metric("Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))

        else:

            with left:

                st.success("✅ LEGITIMATE EMAIL")

                st.markdown("""
## 🟢 Safe Email

No major phishing indicators were detected.

This email appears to be legitimate.

Always verify unexpected emails before sharing sensitive information.
""")

            with right:

                st.metric("Risk Level", "🟢 LOW")
                st.metric("Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))

        st.markdown("---")

        # ----------------------------
        # URL Analysis
        # ----------------------------
        st.subheader("🔗 URL Analysis")

        urls = re.findall(r'https?://\S+|www\.\S+', email)

        if len(urls) > 0:

            st.error("⚠ Suspicious URL(s) Found")

            for url in urls:
                st.code(url)

        else:

            st.success("✅ No URLs Found")

        st.markdown("---")
        if prediction == "spam":

            with left:

                st.error("🚨 PHISHING EMAIL DETECTED")

                st.markdown("""
## ⚠ Security Alert

This email appears to contain phishing or spam characteristics.

### Recommendations

- ❌ Do not click suspicious links
- ❌ Do not download unknown attachments
- ❌ Do not share passwords or OTPs
- ✅ Verify the sender before responding
- ✅ Report suspicious emails to your IT team
""")

            with right:

                st.metric("Risk Level", "🔴 HIGH")
                st.metric("Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))

        else:

            with left:

                st.success("✅ LEGITIMATE EMAIL")

                st.markdown("""
## 🟢 Safe Email

No major phishing indicators were detected.

This email appears to be legitimate.

Always verify unexpected emails before sharing sensitive information.
""")

            with right:

                st.metric("Risk Level", "🟢 LOW")
                st.metric("Confidence", f"{confidence:.2f}%")
                st.progress(int(confidence))

        st.markdown("---")

        # ----------------------------
        # URL Analysis
        # ----------------------------
        st.subheader("🔗 URL Analysis")

        urls = re.findall(r'https?://\S+|www\.\S+', email)

        if len(urls) > 0:

            st.error("⚠ Suspicious URL(s) Found")

            for url in urls:
                st.code(url)

        else:

            st.success("✅ No URLs Found")

        st.markdown("---")
