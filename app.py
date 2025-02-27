import requests
from bs4 import BeautifulSoup
import streamlit as st
import json

# Function to scrape website
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title_tag = soup.find("span", class_="blog-post-title-font blog-post-title-color")
        title = title_tag.get_text(strip=True) if title_tag else "Title Not Found"
        
        # Extract all paragraph content
        paragraphs = soup.find_all("p")
        sentences = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        
        return title, sentences
    except Exception as e:
        return "Error", [f"Error: {str(e)}"]

st.title("Telugu Story Scraper & Noise Filter")

# User input for URL
url = st.text_input("Enter webpage URL to scrape:")
if st.button("Scrape Story", use_container_width=True) and url:
    title, sentences = scrape_website(url)
    
    if title != "Error" and sentences:
        st.session_state['current_story'] = {"title": title, "url": url, "Content": sentences, "category": "stories"}
        st.session_state['temp_noise'] = set()
        st.session_state['edit_mode'] = "checkbox"  # Default selection mode
        st.rerun()
    else:
        st.error("Failed to extract content. Please check the URL and try again.")

if 'current_story' in st.session_state:
    story = st.session_state['current_story']
    st.subheader(story["title"])
    
    # Select mode: Checkbox or Text Editor
    mode = st.radio("Select Editing Mode:", ("Checkbox", "Text Editor"))
    st.session_state['edit_mode'] = mode.lower()
    
    if st.session_state['edit_mode'] == "checkbox":
        selected_sentences = set()
        cleaned_sentences = []
        for idx, paragraph in enumerate(story["Content"]):
            checked = paragraph in st.session_state['temp_noise']
            if st.checkbox(paragraph, key=f'para_{idx}_{hash(story["url"])}', value=checked):
                selected_sentences.add(paragraph)
            else:
                cleaned_sentences.append(paragraph)
    else:
        # Text editor mode
        full_text = "\n".join(story["Content"])
        updated_text = st.text_area("Edit the Story:", full_text, height=300)
        cleaned_sentences = updated_text.split("\n")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save Cleaned Story", use_container_width=True):
            st.session_state['current_story']['Content'] = cleaned_sentences  # Remove noise from UI
            json_data = json.dumps(st.session_state['current_story'], ensure_ascii=False, indent=4)
            safe_title = "_".join(story["title"].split())[:50]  # Limit filename length
            filename = f"{safe_title}.json"
            st.download_button("Download JSON", json_data, filename, "application/json")
    with col2:
        if st.button("➕ Start Fresh", use_container_width=True):
            del st.session_state['current_story']
            del st.session_state['temp_noise']
            del st.session_state['edit_mode']
            st.rerun()
