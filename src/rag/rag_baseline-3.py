# -*- coding: utf-8 -*-
"""RAG_baseline"""

from llama_index.core import (
    Settings,
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)
import yt_dlp
import whisper
import os
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import google.generativeai as genai
import pypdf
import io
import torch
from dotenv import load_dotenv
from pathlib import Path
print("PyTorch version:", torch.__version__)

# Commented out IPython magic to ensure Python compatibility.
# 🔹 Load .env from the SAME folder as this script
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_PROVIDER = os.getenv("API_PROVIDER", "google")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

print("🔍 GEMINI_API_KEY loaded?", "YES" if GEMINI_API_KEY else "NO")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found even after load_dotenv. "
                     "Make sure .env is NEXT TO rag_baseline-3.py")

print(f"✅ Using {API_PROVIDER} with model {MODEL_NAME}")

# test API connection


def test_api_connection():
    try:
        if API_PROVIDER == 'google':
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content("Test")
            print("API connection successful!")
    except Exception as e:
        print(f"API error: {e}")


BASE_DIR = "./data"
PERSIST_DIR = os.path.join(BASE_DIR, "persist")
TRANSCRIPT_DIR = os.path.join(PERSIST_DIR, "transcript")
WEBPAGE_DIR = os.path.join(BASE_DIR, "webpages")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(WEBPAGE_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)
genai.configure(api_key=GEMINI_API_KEY)
print("\n" + "="*70)
print("BUILDING RAG SYSTEM")
print("="*70)

Settings.llm = GoogleGenAI(
    model=MODEL_NAME  # or another valid Gemini model name
)
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="models/embedding-001")  # Corrected model name

print(f"LlamaIndex configured with {MODEL_NAME}")


def download_youtube_video(url, output_path="video.mp4"):
    try:
        yt_ops = {'outtmpl': output_path}
        with yt_dlp.YoutubeDL(yt_ops) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        print(f"❌ Error downloading YouTube video: {e}")
        return None


def upload_mp4():
    path = input("Enter path to your MP4 file (e.g. data/video.mp4): ").strip()
    if not path:
        print("❌ No path provided.")
        return None
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return None
    return path


def transcribe_video(file_path, model_size="medium"):
    try:
        model = whisper.load_model(model_size, device="cpu")
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"❌ Error transcribing video: {e}")
        return None


def save_transcript(text, name):
    try:
        path = os.path.join(TRANSCRIPT_DIR, f"{name}.txt")
        with open(path, "w") as f:
            f.write(text)
        return path
    except Exception as e:
        print(f"❌ Error saving transcript to {path}: {e}")
        return None


def ingest_video_to_rag():
    print("\n🎥 Ingest video into RAG")
    source = input("Paste youtube link or type 'upload' to use MP4: ").strip()

    if source.lower() == 'upload':
        video_path = upload_mp4()
        base_name = os.path.splitext(os.path.basename(video_path))[
            0] if video_path else "uploaded_video"
    else:
        video_path = download_youtube_video(source, output_path="video.mp4")
        base_name = "youtube_video"

    if video_path:
        print("🎙️ Transcribing video...")
        transcript = transcribe_video(video_path)
        if transcript:
            transcript_path = save_transcript(transcript, base_name)

            if transcript_path:
                doc = Document(text=transcript, metadata={
                    "filename": base_name, "source": "video"})
                try:
                    # Check if index exists and merge, or create new
                    if os.path.exists(PERSIST_DIR):
                        # Load existing index
                        storage_context = StorageContext.from_defaults(
                            persist_dir=PERSIST_DIR)
                        index = load_index_from_storage(storage_context)
                        # Add new document to existing index
                        index.insert(doc)
                        print(f"✅ Added transcript to existing index")
                    else:
                        # Create new index
                        index = VectorStoreIndex.from_documents([doc])
                        print(f"✅ Created new index with transcript")

                    # Save updated index
                    index.storage_context.persist(persist_dir=PERSIST_DIR)
                    print(f"💾 Index saved to {PERSIST_DIR}")
                except Exception as e:
                    print(f"❌ Error building or saving index: {e}")


def fetch_youtube_audio_and_transcribe(video_id, output_dir="./audio"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    audio_path = os.path.join(output_dir, f"{video_id}.mp3")

    # Download audio with yt-dlp
    ydl_opts = {"format": "bestaudio/best", "outtmpl": audio_path}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Transcribe audio with Whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"]
    filename = os.path.join(output_dir, f"{video_id}_whisper.txt")
    with open(filename, "w") as f:
        f.write(transcript)
    return Document(text=transcript, metadata={"source": f"YouTube:{video_id}-whisper"})

# === WEBPAGE + CAPTION INGESTION ===


def fetch_webpage_as_document(url):
    print(f"Attempting to fetch webpage: {url}")
    try:
        html = requests.get(url).text
        print("Successfully fetched HTML content.")
        soup = BeautifulSoup(html, "html.parser")
        print("Successfully parsed HTML with BeautifulSoup.")
        clean_text = soup.get_text()
        print(f"Extracted text length: {len(clean_text)}")
        filename = os.path.join(WEBPAGE_DIR, url.replace(
            "https://", "").replace("/", "_") + ".txt")
        print(f"Saving cleaned text to: {filename}")
        with open(filename, "w") as f:
            f.write(clean_text)
        print("Successfully saved cleaned text to file.")
        return Document(text=clean_text, metadata={"source": url})
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching webpage {url}: {e}")
        return None
    except IOError as e:
        print(f"❌ Error writing webpage content to file {filename}: {e}")
        return None
    except Exception as e:
        print(
            f"❌ An unexpected error occurred while processing webpage {url}: {e}")
        return None


def extract_youtube_id(url_or_id: str) -> str:
    """Accept either a full YouTube URL or a raw video ID and return the video ID."""
    text = url_or_id.strip()

    # Already looks like bare ID
    if "youtube.com" not in text and "youtu.be" not in text:
        return text

    try:
        parsed = urlparse(text)
        if "youtube.com" in parsed.netloc:
            qs = parse_qs(parsed.query)
            if "v" in qs:
                return qs["v"][0]

        if "youtu.be" in parsed.netloc:
            return parsed.path.lstrip("/")
    except Exception as e:
        print(f"❌ Error parsing YouTube URL: {e}")

    return text


def fetch_youtube_caption_as_document(url_or_id: str):
    """Fetch YouTube captions and return a LlamaIndex Document, or None if failed."""
    video_id = extract_youtube_id(url_or_id)
    print(f"🎥 Using video ID: {video_id}")

    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id)
        if not entries:
            print("⚠️ No transcript entries returned.")
            return None

        caption_text = "\n".join(e.get("text", "")
                                 for e in entries if e.get("text"))
        print(
            f"✅ Fetched {len(entries)} caption segments, {len(caption_text)} characters.")

        # Make sure transcript directory exists
        os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
        filename = os.path.join(TRANSCRIPT_DIR, f"{video_id}_captions.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(caption_text)

        print(f"💾 Captions saved to: {filename}")
        return Document(text=caption_text, metadata={"source": f"YouTube:{video_id}"})

    except NoTranscriptFound:
        print(f"❌ No transcript found for video {video_id}.")
    except TranscriptsDisabled:
        print(f"❌ Transcripts are disabled for video {video_id}.")
    except VideoUnavailable:
        print(f"❌ Video {video_id} is unavailable.")
    except Exception as e:
        print(
            f"❌ Error fetching YouTube captions for video ID {video_id}: {e}")

    return None


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                text += f"\n[Page {i+1}]\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            except Exception as e:
                print(f"❌ Error extracting text from page {i+1}: {e}")
                text += f"\n[Error extracting text from page {i+1}]\n"
        return text
    except Exception as e:
        print(f"❌ Error reading PDF file: {e}")
        return ""


def add_document_to_index(doc: Document):
    """Add a single Document to the existing index, or create one if none exists."""
    try:
        # Try to load existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print("📚 Loaded existing index. Inserting new document...")
        index.insert(doc)
    except Exception as e:
        print(f"⚠️ Could not load existing index ({e}), creating a new one...")
        index = VectorStoreIndex.from_documents([doc])

    # Persist index
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"💾 Index saved to {PERSIST_DIR}")


def ingest_youtube_captions_to_rag():
    url_or_id = input("Paste YouTube URL or video ID: ").strip()
    if not url_or_id:
        print("❌ No URL/ID provided.")
        return

    doc = fetch_youtube_caption_as_document(url_or_id)
    if doc is None:
        print("⚠️ Could not fetch captions. If the video has no transcript, try the 'Ingest video' option to use Whisper.")
        return

    add_document_to_index(doc)
    print("✅ YouTube captions ingested into RAG!")

# Load Index and Build Query Engine


def upload_and_build_index():
    print("\n📄 Upload your documents (PDF or TXT)")
    print("👉 Put your files into the 'data' folder, then type their names here.")
    print("   Example: mynotes.pdf, book.txt")

    filenames_input = input("Enter filenames (comma-separated): ").strip()
    if not filenames_input:
        print("❌ No filenames provided.")
        return None

    filenames = [name.strip() for name in filenames_input.split(",")]
    documents = []

    for filename in filenames:
        file_path = os.path.join(BASE_DIR, filename)  # BASE_DIR = './data'
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue

        print(f"\n📂 Processing {file_path}")
        try:
            if filename.lower().endswith(".pdf"):
                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                text = extract_text_from_pdf(pdf_bytes)
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

            print(f"✅ Extracted {len(text):,} characters")
            documents.append(
                Document(text=text, metadata={"filename": filename}))
        except Exception as e:
            print(f"❌ Error processing file {filename}: {e}")
            continue

    if not documents:
        print("❌ No documents were successfully processed. Index not built.")
        return None

    print(f"\n📚 Building vector index using {MODEL_NAME} embedding...")
    try:
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print(f"💾 Index has been saved to {PERSIST_DIR}")
        return index
    except Exception as e:
        print(f"❌ Error building or saving index: {e}")
        return None


def load_query_engine(top_k: int = 5):
    try:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        return index.as_query_engine(similarity_top_k=top_k)
    except Exception as e:
        print(f"❌ Error loading index from {PERSIST_DIR}: {e}")
        print("Please ensure you have uploaded documents and built the index first (Option 1).")
        return None


def generate_starup_plan(topic: str, verbose: bool = True) -> str:
    if verbose:
        print("\n" + "="*70)
        print(f"🚀 STARTUP PLAN FOR: {topic}")
        print("="*70)

    query_engine = load_query_engine(top_k=6)
    if not query_engine:
        return "Could not load query engine. Please build the index first."

    prompt = f"""
  You are an experienced startup mentor and VC advisor.

Using ONLY information retrieved from the uploaded documents,
create a structured, data-rich startup plan for:

    **Startup idea:** {topic}

If a section lacks info, write "Not enough information in documents."

Follow this exact format:

**Startup Idea Summary**
- …

**Market Opportunity**
- …

**Location Strategy**
- …

**Budget Estimation**
- …

**Target User Analysis**
- …

**Competitor Snapshot**
- …

**Stage Assessment**
- …

**MVP Features**
- …

**Pricing Model**
- …

**Marketing / GTM Plan**
- …

**Tech Stack Suggestion**
- …

**Funding Advice**
- …

**Risks + Next Milestones**
- …

Base your response on retrieved context; label guesses as (inferred);
cite filenames when possible.
"""
    try:
        response = query_engine.query(prompt)

        if verbose:
            print("\n Generated Startup Plan:\n")
            print(response)
        return str(response)
    except Exception as e:
        print(f"❌ Error generating startup plan: {e}")
        return f"An error occurred while generating the startup plan: {e}"


def query_rag(query: str):
    print("\n Querying RAG system...")
    query_engine = load_query_engine()
    if not query_engine:
        return "Could not load query engine. Please build the index first."
    try:
        response = query_engine.query(query)
        print("\n Response:")
        print(response)
        return str(response)
    except Exception as e:
        print(f"❌ Error during RAG query: {e}")
        return f"An error occurred during the RAG query: {e}"


def main():
    print("\n" + "="*70)
    print(" GEMINI-2.5-FLASH  +  LLAMAINDEX  RAG SYSTEM ")
    print("="*70)
    print("1️⃣  Upload new documents & build index")
    print("2️⃣  Use existing index to generate startup plan")
    print("3️⃣  Query the RAG system")
    print("4️⃣  Ingest webpage or YouTube captions")
    print("5️⃣  Ingest video")

    choice = input("\nChoose an option (1-5):").strip()

    if choice == "1":
        upload_and_build_index()
    elif choice == "2":
        topic = input("Enter your startup idea/topic: ")
        print(generate_starup_plan(topic))
    elif choice == "3":
        q = input("Enter your question: ")
        print(query_rag(q))
    elif choice == "4":
        mode = input(
            "Type 'web' for webpage or 'yt' for YouTube captions: ").strip().lower()
        if mode == "web":
            url = input("Enter webpage URL: ")
            doc = fetch_webpage_as_document(url)
            if doc:
                add_document_to_index(doc)
        elif mode == "yt":
            ingest_youtube_captions_to_rag()
        else:
            print("❌ Invalid mode.")
    elif choice == "5":
        ingest_video_to_rag()
    else:
        print("❌ Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
