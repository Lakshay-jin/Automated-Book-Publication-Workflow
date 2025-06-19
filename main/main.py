import streamlit as st
import os
from scrape import scrape_entire_book
from chroma_manager import add_version
from status_tracker import update_status
from status_tracker import get_status
from ai_writer import spin_chapter
from ai_reviewer import review_chapter
from smart_retriever import feedback,rl_search


CHAPTER_DIR = "book_output"
os.makedirs(CHAPTER_DIR, exist_ok=True)

def get_chapter_list(mode):
    return sorted([
        f for f in os.listdir(CHAPTER_DIR)
        if f.endswith(f"_{mode}.txt")
    ])

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_final_text(chapter_name, final_text):
    final_path = os.path.join(CHAPTER_DIR, chapter_name.replace("_spun.txt", "_final.txt"))
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_text)
    st.success(f"✅ Final version saved to: {final_path}")

st.title("📖 Automated Book Publication")

st.markdown("### Scaping the chapter")

url = st.text_input("Enter ULR of the book you want to scrape", "https://en.wikisource.org/wiki/The_Gates_of_Morning")

if(st.button('Submit')):
    if(scrape_entire_book(url)=="success"):
        st.success("BOOK Scraped successfully")
    else:
        st.error("BOOK was not Scraped")

st.markdown("### spunning and review the chapter")

raw_files=get_chapter_list("raw")
if not raw_files:
    st.warning("No chapters found. Please run the scraper.")
else:
    chapter_cho = st.selectbox("Select Chapter to Review", raw_files)
    if chapter_cho:
        if st.button("Run AI"):
            reviewed_text = review_chapter(spin_chapter(load_file(os.path.join(CHAPTER_DIR, chapter_cho))))
            
            update_status(chapter_cho.replace("_raw.txt", ""), "spun and reviewed")

            # Save reviewed text
            spun_path = os.path.join(CHAPTER_DIR, chapter_cho.replace("_raw.txt", "_spun.txt"))
            with open(spun_path, 'w', encoding='utf-8') as f:
                f.write(reviewed_text)
            chapter_id = chapter_cho.replace("_spun.txt", "")
            add_version(
                chapter_id=chapter_id,
                stage="spun and reviewed",
                text=reviewed_text,
                metadata={"editor": "Human", "source": "streamlit"}
            )

st.markdown("### Human reviewing the chapter")

chapter_files = get_chapter_list("spun")

if not chapter_files:
    st.warning("No chapters found. Please run the scraper + AI writer first.")
else:
    chapter_choice = st.selectbox("Select Chapter to Review", chapter_files)

    if chapter_choice:
        raw_name = chapter_choice.replace("_spun.txt", "_raw.txt")
        raw_path = os.path.join(CHAPTER_DIR, raw_name)
        spun_path = os.path.join(CHAPTER_DIR, chapter_choice)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📜 Original (Raw)")
            st.text_area("Original Chapter", load_file(raw_path), height=400, disabled=True)

        with col2:
            st.subheader("🧠 AI-Spun")
            edited_text = st.text_area("Edit the AI Output", load_file(spun_path), height=400)

        if st.button("💾 Save Final Version"):
            save_final_text(chapter_choice.replace("_spun.txt", ""), edited_text)
            update_status(chapter_choice, "finalized", metadata={"editor": "Lakshay"})

        if st.button("📦 Save Final to ChromaDB"):
            chapter_id = chapter_choice.replace("_spun.txt", "")
            add_version(
                chapter_id=chapter_id,
                stage="final",
                text=edited_text,
                metadata={"editor": "Human", "source": "streamlit"}
            )
            st.success(f"✅ Final version saved in ChromaDB as `{chapter_id}_final`")

    status = get_status(chapter_choice.replace("_spun.txt", ""))
    st.info(f"📌 Current Status: `{status.get('status', 'Unknown')}`\n🕒 Last updated: {status.get('updated_at', 'N/A')}")

st.markdown("### Smart searching for phrases in the chapters")

query = st.text_input("Search for chapters")
if query:
    results = rl_search(query)

    for doc_id, content, meta in results:
        st.markdown(f"### 📖 {doc_id}")
        st.text_area("Excerpt", content[:500] + "...", height=200, key=doc_id, disabled=True)

        if st.button(f"👍 Helpful ({doc_id})"):
            feedback(query, doc_id, reward=1)

        if st.button(f"👎 Not Helpful ({doc_id})"):
            feedback(query, doc_id, reward=-1)
