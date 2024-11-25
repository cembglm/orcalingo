import streamlit as st
from openai import OpenAI
import hashlib
import os
import pickle
from pathlib import Path
import json

# OpenAI API istemcisi
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

if not client.api_key:
    st.error("OpenAI API anahtarı bulunamadı! Lütfen secrets.toml dosyasını doğru yapılandırın.")

# Önbellekleme sistemi için dosya yolu
CACHE_FILE = "cache.pkl"

# Önbelleği yükleme
if Path(CACHE_FILE).exists():
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

# Cache kontrol fonksiyonu
def get_cache_key(*args):
    """Generate a unique key based on function arguments."""
    return hashlib.sha256(str(args).encode()).hexdigest()

def save_to_cache(key, value):
    """Save the result to the cache."""
    cache[key] = value
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

def get_from_cache(key):
    """Retrieve the result from the cache."""
    return cache.get(key)

# Dil bilgisi açıklamaları
gramer_aciklamalari = {
    "Temel Yapılar": {
        "Simple Present": "Geniş zaman, alışkanlıkları ve genel doğruları ifade etmek için kullanılır.",
        "Past Simple": "Geçmişte tamamlanmış olayları ifade etmek için kullanılır.",
        "There is/are": "'Var' anlamını ifade eder ve yer/yokluk belirtir.",
    },
    "İleri Yapılar": {
        "Present Continuous": "Şu anda gerçekleşen olayları ifade etmek için kullanılır.",
        "Future Simple": "Gelecekte yapılacak eylemleri ifade eder ('will' ile).",
        "Present Perfect": "Geçmişte olup etkisi devam eden olayları ifade eder.",
    },
    "Diğer Yapılar": {
        "Passive Voice": "Eylemi yapan değil, eylemin yapıldığı kişi/nesne önemlidir.",
        "Conditionals": "Şartlı cümlelerdir, bir olayın bir diğerine bağlı olduğunu belirtir.",
        "Inversions": "Vurguyu artırmak için kullanılan cümle yapısı değişiklikleridir.",
    },
}

# Kullanıcı arayüzü
st.title("Dil Öğrenme Hikaye Uygulaması")
st.markdown("Seçtiğiniz seçeneklere göre hikayeler oluşturun!")

# Dil ve Seviye Seçimi
st.header("1. Dil ve Seviye Seçimi")
ana_dil = st.selectbox("Ana Dilinizi Seçin:", ["Türkçe", "İngilizce", "Almanca", "Fransızca"])
ogrenilecek_dil = st.selectbox("Öğrenmek İstediğiniz Dili Seçin:", ["İngilizce", "Almanca", "Fransızca", "İspanyolca"])
seviye = st.selectbox("Dil Seviyenizi Seçin:", ["A1", "A2", "B1", "B2", "C1", "C2"])

# Zorluk Seviyesi
st.header("2. Hikaye Hedef Çalışma Stili")
zorluk_seviyesi = st.radio("Çalışma stilini seçin:", ["IELTS", "TOEFL", "Dil Sertifikası", "Günlük Kullanım"])

# Hikaye Türü
st.header("3. Hikaye Türü")
hikaye_turu = st.selectbox("Hangi türde bir hikaye oluşturmak istersiniz?", ["Komedi", "Drama", "Bilim Kurgu", "Macera", "Korku", "Romantik"])

# Gramer Seçimi ve Dil Bilgisi Açıklamaları
st.header("4. Dil Bilgisi Açıklamaları")
with st.expander("Gramer Açıklamaları"):
    for kategori, aciklamalar in gramer_aciklamalari.items():
        st.subheader(kategori)
        for gramer, aciklama in aciklamalar.items():
            st.markdown(f"**{gramer}:** {aciklama}")

secilen_gramer = st.multiselect("Hangi gramer yapılarını dahil etmek istersiniz?", list(gramer_aciklamalari.keys()))

# Karakter Özelleştirme
st.header("5. Hikayede Bulunacak Karakterler")
st.write("Hikayenizde bulunacak karakterleri özelleştirin!")
karakter_secenegi = st.radio(
    "Karakter ekleme seçeneği",
    ["Karakter ekle", "Karakter ekleme"],
    horizontal=True,
    label_visibility="hidden"
)

if karakter_secenegi == "Karakter ekle":
    karakter_sayisi = st.number_input("Kaç karakter eklemek istersiniz?", min_value=1, max_value=10, step=1)
    karakterler = []
    for i in range(karakter_sayisi):
        with st.expander(f"Karakter {i+1} Detayları"):
            isim = st.text_input(f"Karakter {i+1} Adı:", key=f"isim_{i}")
            rol = st.text_input(f"Karakter {i+1} Rolü (ör: baba, arkadaş):", key=f"rol_{i}")
            meslek = st.text_input(f"Karakter {i+1} Mesleği (ör: doktor, öğretmen):", key=f"meslek_{i}")
            karakterler.append({"isim": isim, "rol": rol, "meslek": meslek})
else:
    karakterler = []

# Hikaye Oluşturma
st.header("6. Hikayemizi Oluşturalım")
options = ["Kısa (100 kelime)", "Orta (300 kelime)", "Uzun (500 kelime)"]
hikaye_uzunlugu = st.pills("Hikaye uzunluğunu seçin:", options, selection_mode="single")

# Hikaye Uzunluğunu Prompt'a Dahil Etmek
uzunluk_limitleri = {
    "Kısa (100 kelime)": 100,
    "Orta (300 kelime)": 300,
    "Uzun (500 kelime)": 500}

if st.button("Hikaye Oluştur"):
    # Kullanıcının seçim yapmadığı durumu kontrol et
    if not hikaye_uzunlugu:
        st.warning("Lütfen bir hikaye uzunluğu seçin.")
    else:
        with st.spinner("Hikaye oluşturuluyor, lütfen bekleyin..."):
            try:
                karakter_detaylari = ". ".join(
                    [f"{k['isim']} is a {k['rol']} and works as a {k['meslek']}."
                    for k in karakterler if k['isim']]
                )

                # JSON formatında yanıt istemek için prompt düzenlemesi
                prompt = {
                    "instruction": f"""
                    Create a story in {ogrenilecek_dil} for a learner at {seviye} level. 
                    Include the following grammar structures: {', '.join(secilen_gramer)}.
                    Make the story appropriate for {zorluk_seviyesi} preparation. 
                    Include these characters: {karakter_detaylari}.
                    Translate the story into {ana_dil}.
                    Ensure the story is approximately {uzunluk_limitleri[hikaye_uzunlugu]} words.
                    Provide the output in JSON format with the keys:
                    - "original_story" for the story in {ogrenilecek_dil}.
                    - "translated_story" for the story in {ana_dil}.
                    """
                }

                # Cache kontrolü
                cache_key = get_cache_key(json.dumps(prompt))
                cached_response = get_from_cache(cache_key)
                if cached_response:
                    response_json = cached_response
                else:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": json.dumps(prompt)}
                        ],
                        max_tokens=1500,
                        temperature=0.7
                    )
                    response_json = json.loads(response.choices[0].message.content)
                    save_to_cache(cache_key, response_json)

                st.session_state["story"] = response_json

                # Hikaye Gösterimi (JSON'dan ayrıştırma)
                with st.expander(f"Hikaye ({ogrenilecek_dil})"):
                    st.write(response_json.get("original_story", "Hikaye alınamadı."))
                with st.expander(f"Hikaye Çevirisi ({ana_dil})"):
                    st.write(response_json.get("translated_story", "Çeviri alınamadı."))

            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")


# Hikayedeki Önemli Kelimeler
st.header("7. Hikayemizdeki Önemli Kelimeler ve Çevirileri")
if "story" in st.session_state:
    try:
        # Prompt'u açık ve net bir şekilde yapılandırma
        story_content = st.session_state["story"].get("original_story", "")
        kelime_prompt = f"""
        Extract 10 important words from the story below and translate them into {ana_dil}.
        The output should be a JSON array of objects with two keys: 
        - "word" (the important word in {ogrenilecek_dil})
        - "translation" (the translation of the word in {ana_dil}).

        Example Output:
        [
            {{"word": "apple", "translation": "elma"}},
            {{"word": "book", "translation": "kitap"}}
        ]

        Story: {story_content}
        """

        kelime_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts words and provides translations."},
                {"role": "user", "content": kelime_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Yanıtı kontrol et ve JSON'a dönüştür
        raw_content = kelime_response.choices[0].message.content.strip()

        try:
            # Çift tırnaklar içinde JSON stringini gerçek JSON formatına dönüştür
            if raw_content.startswith("```json"):
                raw_content = raw_content.strip("```json").strip()
            kelimeler_json = json.loads(raw_content)
        except json.JSONDecodeError:
            raise ValueError(f"Yanıt JSON formatında değil. Alınan yanıt: {raw_content}")

        # Kelimeleri ve çevirileri göster
        for kelime in kelimeler_json:
            yabanci_kelime = kelime.get("word", "Bilinmiyor")
            ceviri = kelime.get("translation", "Bilinmiyor")
            st.markdown(f"**{yabanci_kelime}**: {ceviri}")

    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")
else:
    st.info("Önce bir hikaye oluşturmalısınız.")

# Sesli Anlatım
st.header("8. Hikayemizi Dinleyelim")
if "story" in st.session_state:
    voice = st.selectbox("Ses Seçimi:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
    if st.button("Sesli Anlatımı Başlat"):
        with st.spinner("Sesli anlatım hazırlanıyor..."):
            try:
                speech_file_path = Path("hikaye.mp3")
                speech_response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=st.session_state["story"]
                )
                speech_response.stream_to_file(speech_file_path)
                st.audio(str(speech_file_path))

            except Exception as e:
                st.error(f"Sesli anlatım oluşturulurken bir hata oluştu: {str(e)}")
else:
    st.info("Sesli anlatım için önce bir hikaye oluşturmalısınız.")

# Görsel Oluşturma
st.header("9. Hikayemizi Görelim")
if "story" in st.session_state:
    if st.button("Hikaye için Görsel Oluştur"):
        with st.spinner("Görsel oluşturuluyor..."):
            try:
                dall_e_response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"{hikaye_turu} story illustration with {', '.join([k['isim'] for k in karakterler if k['isim']])}",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = dall_e_response.data[0].url
                st.image(image_url)

            except Exception as e:
                st.error(f"Görsel oluşturulurken bir hata oluştu: {str(e)}")
else:
    st.info("Görsel oluşturmak için önce bir hikaye oluşturmalısınız.")
