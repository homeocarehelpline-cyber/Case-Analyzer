# যখন বাটন ক্লিক করা হবে
if submit_button:
    if not api_key:
        st.error("⚠️ অনুগ্রহ করে সাইডবারে আপনার Gemini API Key দিন।")
    elif not case_text and not uploaded_images:
        st.warning("⚠️ বিশ্লেষণ করার জন্য রোগীর কোনো লক্ষণ লিখুন অথবা ছবি আপলোড করুন।")
    else:
        genai.configure(api_key=api_key)
        
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
                # সরাসরি জেমিনির যেকোনো উপলব্ধ মডেল খুঁজে নেওয়ার কোড
                model = None
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        if 'flash' in m.name or 'pro' in m.name:
                            model = genai.GenerativeModel(m.name)
                            break
                
                if not model:
                    model = genai.GenerativeModel('gemini-pro')

                if uploaded_images:
                    content = [prompt, case_text] + uploaded_images
                    response = model.generate_content(content)
                else:
                    response = model.generate_content([prompt, case_text])
                
                st.success("✅ বিশ্লেষণ সম্পন্ন হয়েছে!")
                st.markdown("### 📊 AI Analysis Report")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"⚠️ একটি সমস্যা হয়েছে: {e}")
