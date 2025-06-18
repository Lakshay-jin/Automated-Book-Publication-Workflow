from gemini_api import call_gemini

def review_chapter(text):
    prompt = f"Act as an editor and refine this chapter:\n{text}"
    return "Reviewed version of: " + call_gemini(prompt)
