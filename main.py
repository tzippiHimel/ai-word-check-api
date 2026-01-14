import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# הגדרת מפתח ה-API
# שים לב: אם לא הגדרת Environment Variable ב-Render, שים את המפתח כאן במקום המחרוזת
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@app.route('/check-ai', methods=['POST'])
def check_ai():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400

        text_to_ai = data.get('text_to_ai')
        word_to_check = data.get('word_to_check')

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(text_to_ai)
        ai_text = response.text

        is_found = word_to_check.lower() in ai_text.lower()

        return jsonify({
            "ai_response": ai_text,
            "word_found": is_found
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# החלק הקריטי להרצה ב-Render:
if __name__ == "__main__":
    # Render חייב לקבל את הפורט ממשתנה הסביבה
    port = int(os.environ.get("PORT", 10000))
    # ה-host חייב להיות 0.0.0.0 כדי שיהיה ציבורי
    app.run(host='0.0.0.0', port=port)


