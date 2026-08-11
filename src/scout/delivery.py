import os
import httpx
from scout.db import get_connection

def get_telegram_credentials():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    # Try reading from a .env file if not set in environment
    if not token or not chat_id:
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        token = line.strip().split("=")[1]
                    elif line.startswith("TELEGRAM_CHAT_ID="):
                        chat_id = line.strip().split("=")[1]
        except FileNotFoundError:
            pass
            
    return token, chat_id

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = httpx.post(url, json=payload)
    response.raise_for_status()

def run_delivery():
    print("Starting SCOUT Phase 0 Dummy Delivery...")
    token, chat_id = get_telegram_credentials()
    
    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found.")
        print("Please set them in your environment or in a .env file.")
        return
        
    conn = get_connection()
    try:
        # Get the latest unsent opportunity from the last 24 hours
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, problem_description, score 
            FROM opportunities 
            WHERE sent_at IS NULL AND created_at >= datetime('now', '-24 hours')
            ORDER BY score DESC LIMIT 1
            """
        )
        row = cursor.fetchone()
        
        if row:
            message = f"<b>SCOUT DAILY BRIEF</b> 🚀\n\n"
            message += f"<b>Top Opportunity:</b> {row['title']}\n"
            message += f"<b>Score:</b> {row['score']}/10\n"
            message += f"<b>Problem:</b> {row['problem_description']}\n"
            
            print(f"Sending message for opportunity: {row['title']}")
            send_telegram_message(token, chat_id, message)
            
            # Mark as sent
            cursor.execute(
                "UPDATE opportunities SET sent_at = CURRENT_TIMESTAMP WHERE id = ?",
                (row['id'],)
            )
            conn.commit()
            print("Message sent successfully.")
        else:
            print("No unsent opportunities found.")
            
    except Exception as e:
        print(f"Delivery failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_delivery()
