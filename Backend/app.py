import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

PROMPT_TEMPLATES = {
    "linkedin": """You are a professional content writer who specializes in engaging, authentic LinkedIn posts.

Write a LinkedIn post about the following topic: "{topic}"

Guidelines:
- Start with a strong hook in the first line to grab attention
- Keep the tone professional but conversational
- Include 2-3 key points, insights, or highlights related to the topic
- End with a question or call-to-action that encourages engagement
- Include 4-5 relevant hashtags at the end
- Keep the total length between 100-200 words
- Do not use excessive emojis — at most 1-2, if any""",

    "instagram": """You are a social media writer who specializes in magnificent Instagram posts.

Write an Instagram caption about the following topic: "{topic}"

Guidelines:
- Keep it brief — one or two lines
- Tone should be warm, playful, and relatable
- Don't make it sound too artificial — keep it natural and human
- Use 3-4 relevant hashtags
- Use 1-2 emojis naturally, where they fit""",

    "blog": """You are an experienced blog writer who specializes in engaging, thoughtful introductions.

Write a blog post introduction about the following topic: "{topic}"

Guidelines:
- Open with a hook — a question, a surprising fact, or a relatable scenario
- Explain briefly why this topic matters or is worth reading about
- Set expectations for what the reader will learn or gain
- Tone should be thoughtful, conversational, and confident
- Keep it to 3-5 sentences, roughly 80-120 words
- End with a smooth transition line"""
}


def init_db():
    connection = sqlite3.connect("history.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT,
            topic TEXT,
            output TEXT,
            created_at TEXT
        )
    """)
    connection.commit()
    connection.close()


init_db()


@app.route("/generate", methods=["POST"])
def generate_content():
    data = request.get_json()
    topic = data.get("topic")
    content_type = data.get("content_type")

    template = PROMPT_TEMPLATES.get(content_type)

    if not template:
        return jsonify({"error": "Invalid content type"}), 400

    final_prompt = template.format(topic=topic)

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=final_prompt
        )
        output_text = response.text
    except Exception as e:
        return jsonify({"error": "Something went wrong generating content. Please try again."}), 500


    connection = sqlite3.connect("history.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO history (content_type, topic, output, created_at) VALUES (?, ?, ?, ?)",
        (content_type, topic, output_text, datetime.now().isoformat())
    )
    connection.commit()
    connection.close()

    return jsonify({"reply": output_text})


@app.route("/history", methods=["GET"])
def get_history():
    connection = sqlite3.connect("history.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, content_type, topic, output, created_at FROM history ORDER BY id DESC")
    rows = cursor.fetchall()
    connection.close()

    history_list = []
    for row in rows:
        history_list.append({
            "id": row[0],
            "content_type": row[1],
            "topic": row[2],
            "output": row[3],
            "created_at": row[4]
        })

    return jsonify(history_list)


if __name__ == "__main__":
    app.run(debug=True)
