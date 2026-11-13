import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

player_data = {}

@app.route("/", methods=["GET"])
def home():
    return "Roblox AI Guard Server is running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        player_id = str(data.get("player_id", "default_player"))
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"reply": "Silence will not open these gates. Speak up!"})

        if player_id not in player_data:
            player_data[player_id] = {"attempts": 0}

        player_data[player_id]["attempts"] += 1
        attempts = player_data[player_id]["attempts"]

        if attempts >= 20:
            return jsonify({"reply": "[BAN] Guards! Throw this nuisance out of the castle immediately!"})

        if attempts <= 5:
            mood = "You are a stern, suspicious castle gate guard. You are hard to convince, but polite."
        elif attempts <= 10:
            mood = "You are getting annoyed and losing your patience with this person at the gate."
        else:
            mood = "You are extremely angry, furious, and ready to ban this person."

        prompt = f"""
        {mood}
        The player is trying to persuade you to open the castle gate.
        Player's message: "{message}"
        Attempt count: {attempts} out of 20.
        If the player successfully persuades you with a brilliant argument, start your response with [WIN].
        Otherwise, reply in character as the guard keeping the gate closed, keeping the response under 40 words.
        """

        response = model.generate_content(prompt)
        reply = response.text.strip()
        return jsonify({"reply": reply, "attempts": attempts})
        
    except Exception as e:
        return jsonify({"reply": f"Guard AI Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
