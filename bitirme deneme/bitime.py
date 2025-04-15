import os
from dotenv import load_dotenv
from groq import Groq
import pdfplumber

# .env dosyasını yükle
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Grok istemcisini oluştur
client = Groq(api_key=groq_api_key)

def summarize_text(text, max_tokens=4000):
    # Metni token sayısına göre parçalara böl
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Her parçayı Türkçe olarak özetle
    summaries = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Türkçe metinleri özetleyen bir asistansın. Özetleri yalnızca Türkçe olarak üret."},
                {"role": "user", "content": f"Lütfen aşağıdaki metni Türkçe olarak özetle:\n\n{chunk}"}
            ],
            max_tokens=150,
            temperature=0.7,
            top_p=1.0
        )
        summaries.append(response.choices[0].message.content.strip())

    # Özetleri birleştir
    return " ".join(summaries)

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text

if __name__ == "__main__":
    pdf_path = "makale.pdf"
    article_text = extract_text_from_pdf(pdf_path)
    summary = summarize_text(article_text)
    print("Makale Özeti:\n", summary)