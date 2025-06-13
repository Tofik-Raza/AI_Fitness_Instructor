from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)
CORS(app)

# Load Nutrition Model
nutrition_model = joblib.load("model/NeuralNet_pipeline.pkl")

# Load Phi-2
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
phi_model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype=torch.float32)
phi_model.eval()
print("Phi-2 model loaded.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()
    prompt = data.get("prompt", "")

    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = phi_model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            top_p=0.9,
            temperature=0.7
        )

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return jsonify({"response": response})

@app.route("/api/nutrition", methods=["POST"])
def get_nutrition():
    data = request.get_json()
    required_fields = ["age", "height", "weight", "sex", "activity_level"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields in input"}), 400

    input_df = pd.DataFrame([{
        "age": data["age"],
        "height": data["height"],
        "weight": data["weight"],
        "sex": data["sex"],
        "activity_level": data["activity_level"]
    }])

    preds = nutrition_model.predict(input_df)[0]
    response = {
        "calories": round(preds[0], 2),
        "protein": round(preds[1], 2),
        "fat": round(preds[2], 2),
        "carbs": round(preds[3], 2)
    }

    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
