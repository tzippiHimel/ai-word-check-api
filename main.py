import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# הגדרת מפתח API - מומלץ להגדיר ב-Render תחת Environment Variables
# אם אתה שם אותו פה ישירות, שים אותו במקום ה-YOUR_API_KEY
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "YOUR_ACTUAL_API_KEY_HERE"))

@app.route('/check-ai', methods=['POST'])
def check_ai():
    try:
        # קבלת נתונים מהבקשה
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        text_to_ai = data.get('text_to_ai')
        word_to_check = data.get('word_to_check')

        # בדיקה שהפרמטרים קיימים
        if not text_to_ai or not word_to_check:
            return jsonify({"error": "Missing parameters 'text_to_ai' or 'word_to_check'"}), 400

        # פנייה ל-AI (Gemini)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(text_to_ai)
        ai_text = response.text

        # בדיקה האם המילה מופיעה בתשובה
        is_found = word_to_check.lower() in ai_text.lower()

        # החזרת התוצאה הנדרשת
        return jsonify({
            "ai_response": ai_text,
            "word_found": is_found,
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # הגדרות הרצה שמתאימות לענן
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
