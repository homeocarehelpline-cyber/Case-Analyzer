import streamlit as st
import google.generativeai as genai
from PIL import Image

# ওয়েবসাইটের পেজ কনফিগারেশন
st.set_page_config(page_title="Dr. Rahman's Homeopathy AI", page_icon="🩺", layout="wide")

st.title("🩺 Homeopathic AI Case Analyzer")
st.markdown("রোগীর লক্ষণগুলো নিচে লিখুন অথবা পূর্বের প্রেসক্রিপশন / প্যাথলজি রিপোর্টের ছবি আপলোড করুন।")

# সাইডবারে API Key ইনপুট নেওয়ার ব্যবস্থা (যাতে কোডে সরাসরি কি না থাকে)
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="আপনার Google AI Studio থেকে পাওয়া API Key এখানে দিন")
    st.markdown("---")
    st.markdown("### নির্দেশনা:")
    st.markdown("১. রোগীর মানসিক ও শারীরিক লক্ষণ বিস্তারিত লিখুন।\n২. রোগীর কোনো ছবি বা টেস্ট রিপোর্ট থাকলে আপলোড করুন।\n৩. 'Analyze Case' বাটনে ক্লিক করুন।")

# কেইস ইনপুটের জন্য ফর্ম
with st.form("case_form"):
    st.subheader("📝 রোগীর বর্তমান অবস্থা ও লক্ষণ")
    
    # মাল্টিলাইন টেক্সট এরিয়া (এখানে এলোমেলোভাবে সব লেখা যাবে)
    case_text = st.text_area(
        "রোগীর বিস্তারিত বিবরণ (মানসিক, শারীরিক, খাবার, ঘুম, ঘাম ইত্যাদি):", 
        height=200, 
        placeholder="উদাহরণ: রোগীর খুব শীত লাগে, সবসময় রাগ করে থাকে, ডিম পছন্দ করে..."
    )
    
    st.subheader("📎 ছবি বা রিপোর্ট আপলোড (ঐচ্ছিক)")
    # ইমেজ বা রিপোর্ট আপলোড করার ফাইল আপলোডার
    uploaded_files = st.file_uploader(
        "রোগীর ছবি, প্যাথলজি রিপোর্ট বা পুরনো প্রেসক্রিপশন আপলোড করুন", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    # ফর্ম সাবমিট বাটন
    submit_button = st.form_submit_button("🔍 Analyze Case")

# যদি আপলোড করা ফাইল থাকে, তবে সেগুলো স্ক্রিনে দেখানো
uploaded_images = []
if uploaded_files:
    st.subheader("📸 আপলোড করা ডকুমেন্টস:")
    cols = st.columns(len(uploaded_files))
    for idx, file in enumerate(uploaded_files):
        img = Image.open(file)
        uploaded_images.append(img)
        # আপলোড করা ছবিগুলো স্ক্রিনে দেখানো হচ্ছে
        cols[idx].image(img, caption=file.name, use_column_width=True)

# যখন বাটন ক্লিক করা হবে
if submit_button:
    if not api_key:
        st.error("⚠️ অনুগ্রহ করে সাইডবারে আপনার Gemini API Key দিন।")
    elif not case_text and not uploaded_images:
        st.warning("⚠️ বিশ্লেষণ করার জন্য রোগীর কোনো লক্ষণ লিখুন অথবা ছবি আপলোড করুন।")
    else:
        # API Key সেট করা
        genai.configure(api_key=api_key)
        
        # আমরা জেমিনির লেটেস্ট ফ্ল্যাশ মডেল ব্যবহার করব, যা ছবি এবং টেক্সট দুটোই বুঝতে পারে
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # দ্য মাস্টার প্রম্পট
        prompt = """
        তুমি এখন একজন এক্সপার্ট ক্লাসিক্যাল হোমিওপ্যাথ (জর্জ ভিথুলকাসের মেথড অনুযায়ী)। আমি তোমাকে নিচে একটি কেইস হিস্ট্রি এবং/অথবা রোগীর কিছু রিপোর্ট/ছবি দিচ্ছি। 
        তুমি সরাসরি কোনো ওষুধের নাম বলবে না বা উপসংহারে পৌঁছাবে না। তোমাকে অবশ্যই নিচের ৪টি ধাপে কেইসটি বিশ্লেষণ করতে হবে:
        
        ধাপ ১ (লক্ষণের মূল্যায়ন): কেইসটি (এবং ছবির তথ্য) থেকে মানসিক, শারীরিক সাধারণ (বিশেষ করে কাতরতা) এবং অদ্ভুত/বিরল লক্ষণগুলো আলাদা করো এবং কেন্টের হায়ারার্কি অনুযায়ী সাজাও।
        ধাপ ২ (কেইসের কেন্দ্রবিন্দু): রোগীর মূল সমস্যা বা 'Center of gravity' কোথায় সেটি এক লাইনে লেখো।
        ধাপ ৩ (ডিফারেনশিয়াল ডায়াগনোসিস): লক্ষণগুলোর ওপর ভিত্তি করে অন্তত ৩টি থেকে ৪টি সম্ভাব্য ওষুধের নাম লেখো এবং তাদের তুলনামূলক পার্থক্য (Differential Diagnosis) করো।
        ধাপ ৪ (চূড়ান্ত নির্বাচন): মেটিরিয়া মেডিকার ওপর ভিত্তি করে সবচেয়ে উপযুক্ত একটি সিঙ্গেল মেডিসিন (Simillimum) নির্বাচন করো এবং ঠিক কোন ১টি বা ২টি সুনির্দিষ্ট লক্ষণের কারণে অন্য ওষুধগুলো বাদ পড়ল, তা স্পষ্টভাবে ব্যাখ্যা করো।
        
        রোগীর বিবরণ নিচে দেওয়া হলো:
        """
        
        with st.spinner("AI বিশ্লেষণ করছে... দয়া করে অপেক্ষা করুন..."):
            try:
                # যদি ছবি থাকে তবে ছবি এবং টেক্সট একসাথে পাঠাবে
                if uploaded_images:
                    content = [prompt, case_text] + uploaded_images
                    response = model.generate_content(content)
                else:
                    # ছবি না থাকলে শুধু টেক্সট পাঠাবে
                    response = model.generate_content([prompt, case_text])
                
                # ফলাফল প্রদর্শন
                st.success("✅ বিশ্লেষণ সম্পন্ন হয়েছে!")
                st.markdown("### 📊 AI Analysis Report")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"⚠️ একটি সমস্যা হয়েছে: {e}")
