from gemini_api import call_gemini

def spin_chapter(text):
    prompt = f"Rewrite the following chapter with improved narrative tone:\n{text}"
    return "Spun version of: " + call_gemini(prompt)
    
