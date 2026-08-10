def is_junk(title: str, content: str) -> bool:
    """
    Very fast, cheap heuristic filter to drop obvious non-problems 
    before sending to the expensive LLM.
    """
    
    # 1. Too short (unlikely to describe a detailed problem)
    if len(content.split()) < 15:
        return True
        
    # 2. Too long (might be a massive log file or book, too expensive to process)
    if len(content.split()) > 2000:
        return True
        
    # 3. Simple spam or promotion keywords
    lower_content = content.lower()
    spam_keywords = ["buy now", "subscribe to my", "discount code", "click here"]
    if any(keyword in lower_content for keyword in spam_keywords):
        return True
        
    # 4. Job postings (Ask HN: Who is hiring?)
    if "who is hiring" in title.lower() or "freelancer seeking" in title.lower():
        return True
        
    return False
