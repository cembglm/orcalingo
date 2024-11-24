import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
import requests

# .env dosyasını yükle
load_dotenv()

# OpenAI API istemcisi
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not client.api_key:
    st.error("OpenAI API anahtarı bulunamadı! Lütfen .env dosyasını doğru yapılandırın.")

# Kelime ve gramer verileri
kelime_verisi = {
    "A1": ["hello", "world", "apple", "school", "friend"],
    "A2": ["travel", "book", "restaurant", "family", "weekend"],
    "B1": ["opportunity", "decision", "experience", "project", "future"],
    "B2": ["analysis", "consequence", "perspective", "strategy", "negotiation"],
    "C1": ["innovation", "collaboration", "philosophy", "leadership", "phenomenon"],
    "C2": ["sustainability", "paradigm", "aesthetic", "existentialism", "dialectical"]
}

gramer_verisi = {
    "A1": ["Present Simple", "Past Simple", "There is/are"],
    "A2": ["Present Continuous", "Future Simple", "Modal Verbs (can, must)"],
    "B1": ["Present Perfect", "Past Continuous", "Conditionals (Type 1)"],
    "B2": ["Passive Voice", "Conditionals (Type 2)", "Reported Speech"],
    "C1": ["Advanced Passive Structures", "Mixed Conditionals", "Subjunctive Mood"],
    "C2": ["Inversions", "Advanced Modals", "Cleft Sentences"]
}

konular = [
    "Günlük Hayat", "Seyahat", "İş ve Kariyer", "Eğitim", "Sağlık",
    "Doğa ve Çevre", "Bilim ve Teknoloji", "Sanat ve Kültür", "Tarih",
    "Aile ve İlişkiler", "Spor", "Eğlence", "Politika", "Yemek Tarifleri"
]

# Streamlit Uygulaması
st.title("Dil Öğrenme Hikaye Uygulaması")
st.markdown("Seçtiğiniz dil ve seviyeye uygun hikayeler oluşturun!")

# Dil ve Seviye Seçimi
st.header("1. Dil ve Seviye Seçimi")
ana_dil = st.selectbox("Ana Dilinizi Seçin:", ["Türkçe", "İngilizce", "Almanca", "Fransızca"])
ogrenilecek_dil = st.selectbox("Öğrenmek İstediğiniz Dili Seçin:", ["İngilizce", "Almanca", "Fransızca", "İspanyolca"])
seviye = st.selectbox("Dil Seviyenizi Seçin:", ["A1", "A2", "B1", "B2", "C1", "C2"])

# Konu Seçimi
st.header("2. Hikaye Konusunu Seçin")
secili_konu = st.selectbox("Hangi konuda bir hikaye oluşturmak istersiniz?", konular)

# Hikaye Uzunluğu Seçimi
st.header("3. Hikaye Uzunluğu")
hikaye_uzunlugu = st.selectbox("Hikaye uzunluğunu seçin:", ["Kısa", "Orta", "Uzun"])

# Kelime ve Gramer Gösterimi
st.header("4. Kelime ve Gramer Yapıları")
kelimeler = kelime_verisi[seviye]
gramer_listesi = gramer_verisi[seviye]

st.markdown(f"Seçilen seviye: {seviye}")
st.write("Kelimeler: ", ", ".join(kelimeler))
secilen_gramer = st.selectbox("Hikayede kullanılmasını istediğiniz gramer yapısını seçin:", gramer_listesi)

# Hikaye Oluşturma
st.header("5. Hikaye Oluşturma")
if st.button("Hikaye Oluştur"):
    with st.spinner("Hikaye oluşturuluyor, lütfen bekleyin..."):
        try:
            # ChatCompletion için doğru prompt
            prompt = f"""
            Write a {hikaye_uzunlugu} story in {ogrenilecek_dil} for a {seviye} level learner about {secili_konu}.
            Include the following vocabulary: {', '.join(kelimeler)}. Use the grammatical structure: {secilen_gramer}.
            Provide a clear translation of the story in {ana_dil} ({ana_dil}). Ensure the translation is in {ana_dil}.
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates language learning stories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            # Yanıtı işleme
            story_parts = response.choices[0].message.content.split("\n\n")
            giris = story_parts[0] if len(story_parts) > 0 else "Giriş bölümü bulunamadı."
            gelisme = story_parts[1] if len(story_parts) > 1 else "Gelişme bölümü bulunamadı."
            sonuc = story_parts[2] if len(story_parts) > 2 else "Sonuç bölümü bulunamadı."

            # Çeviriler ve hikaye
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"Hikaye ({ogrenilecek_dil})")
                st.write(f"Giriş: {giris}")
                st.write(f"Gelişme: {gelisme}")
                st.write(f"Sonuç: {sonuc}")

            with col2:
                st.subheader(f"Hikaye Çevirisi ({ana_dil})")
                # Orijinal çeviri, Türkçe'ye odaklanarak düzeltilmiştir.
                st.write(f"Giriş: {giris}")
                st.write(f"Gelişme: {gelisme}")
                st.write(f"Sonuç: {sonuc}")

            # # Sesli Anlatım
            # speech_file_path = Path("hikaye.mp3")
            # speech_response = client.audio.speech.create(
            #     model="tts-1",
            #     voice="alloy",
            #     input=f"{giris} {gelisme} {sonuc}"
            # )
            # speech_response.stream_to_file(speech_file_path)

            # st.audio(str(speech_file_path))

            # # Görsel Oluşturma
            # st.header("Hikaye için Görsel")
            # dall_e_response = client.images.generate(
            #     model="dall-e-3",
            #     prompt=f"{secili_konu}, as a story illustration",
            #     size="1024x1024",
            #     quality="standard",
            #     n=1,
            # )
            # image_url = dall_e_response.data[0].url
            # st.image(image_url)

        except Exception as e:
            st.error(f"Hikaye oluşturulurken bir hata oluştu: {str(e)}")
