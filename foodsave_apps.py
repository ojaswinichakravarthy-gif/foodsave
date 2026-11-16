import streamlit as st
from PIL import Image
import numpy as np
import requests
import base64

st.set_page_config(page_title="FoodSave - Reduce Food Waste", layout="centered")

st.title("🍽 FoodSave - AI Recipe Recommender")
st.write("Upload a picture of your leftover or available food items and get recipe suggestions to reduce food waste!")

uploaded_image = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

API_KEY = "YOUR_CLARIFAI_API_KEY"  # Replace with your Clarifai API key
MODEL_ID = "food-item-recognition"  # Example model

def image_to_base64(image):
    buffered = image.convert("RGB")
    img_bytes = buffered.tobytes()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64

def predict_ingredients_clarifai(img):
    buffered = img.convert("RGB")
    buffered.save("temp.jpg")  # Save image locally for sending to API
    with open("temp.jpg", "rb") as image_file:
        image_bytes = image_file.read()

    headers = {
        "Authorization": f"Key {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "inputs": [
            {
                "data": {
                    "image": {
                        "base64": base64.b64encode(image_bytes).decode("utf-8")
                    }
                }
            }
        ]
    }

    response = requests.post(
        f"https://api.clarifai.com/v2/models/{MODEL_ID}/outputs",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        predictions = response.json()['outputs'][0]['data']['concepts']
        return [p['name'] for p in predictions[:5]]  # Top 5 ingredients
    else:
        return []

def get_recipes(ingredients):
    sample_recipes = {
        'banana': ["Banana Smoothie", "Banana Pancakes"],
        'broccoli': ["Broccoli Stir Fry", "Broccoli Soup"],
        'carrot': ["Carrot Salad", "Carrot Halwa"],
        'cheese': ["Mac and Cheese", "Grilled Cheese Sandwich"],
        'tomato': ["Tomato Soup", "Pasta with Tomato Sauce"],
        'potato': ["Baked Potato", "Mashed Potatoes"],
        'onion': ["Onion Rings", "French Onion Soup"]
    }
    suggested = set()
    for item in ingredients:
        for key in sample_recipes:
            if key in item.lower():
                suggested.update(sample_recipes[key])
    return list(suggested) if suggested else ["No matching recipes found. Try entering ingredients manually."]

# Image processing
if uploaded_image is not None:
    img = Image.open(uploaded_image)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing image and fetching ingredients..."):
        ingredients = predict_ingredients_clarifai(img)

    if ingredients:
        st.success(f"Identified ingredients: {', '.join(ingredients)}")
    else:
        st.warning("Could not identify ingredients. Please enter them manually.")

    # Manual fallback or edit option
    manual_input = st.text_input("Edit or enter ingredients manually (comma-separated):")
    if manual_input:
        ingredients = [x.strip().lower() for x in manual_input.split(",")]

    if ingredients:
        st.subheader("🍳 Recipe Suggestions:")
        recipes = get_recipes(ingredients)
        for recipe in recipes:
            st.markdown(f"- {recipe}")