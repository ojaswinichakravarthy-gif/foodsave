import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np
import requests
import re

# Config
st.set_page_config(page_title="Smart Food Classifier", layout="centered")
SPOON_KEY = "33647b5804764c36b1634eb78a49e4f5"
MODEL_PATH = "food101_efficientnetb0.h5"  # Replace with actual path if downloading

# HTML remover
def clean_html(s): return re.sub('<.*?>', '', s or "")

# Load model
@st.cache(allow_output_mutation=True)
def load_model():
    model = tf.keras.applications.EfficientNetB0(include_top=True, weights=None, classes=101)
    model.load_weights(MODEL_PATH)
    return model
model = load_model()

# Map Food-101 classes
food_classes = []
with open("labels_food101.txt") as f:
    food_classes = [line.strip() for line in f]

# Predict food items
def get_food_predictions(img):
    img = img.resize((224,224))
    x = tf.keras.applications.efficientnet.preprocess_input(np.array(img)[None])
    preds = model.predict(x)[0]
    # Get up to top 5 with threshold
    items = [food_classes[i] for i in np.argsort(preds)[-5:][::-1] if preds[i] > 0.1]
    return items

# Spoonacular recipe fetch
def get_recipes(items):
    recipes = []
    seen_ids = set()
    for it in items:
        q = it.replace(" ", "+")
        url = f"https://api.spoonacular.com/recipes/complexSearch?query={q}&number=2&apiKey={SPOON_KEY}"
        res = requests.get(url)
        if res.status_code != 200: continue
        for r in res.json().get("results", []):
            rid = r["id"]
            if rid in seen_ids: continue
            seen_ids.add(rid)
            d = requests.get(f"https://api.spoonacular.com/recipes/{rid}/information?apiKey={SPOON_KEY}").json()
            recipes.append({
                "title": d.get("title"),
                "url": d.get("sourceUrl"),
                "summary": clean_html(d.get("summary","")),
                "instructions": d.get("instructions","No instructions.")
            })
    return recipes

# UI
st.title("🍲 Food Classifier + Recipes")
file = st.file_uploader("Upload food image", type=["jpg","png","jpeg"])
if file:
    img = Image.open(file).convert("RGB")
    st.image(img, caption="Uploaded", use_column_width=True)

    with st.spinner("Analyzing image for food..."):
        foods = get_food_predictions(img)
    if not foods:
        st.warning("No recognizable food detected.")
    else:
        st.success(f"Detected: {', '.join(foods)}")
        with st.spinner("Fetching recipes..."):
            recs = get_recipes(foods)
        if recs:
            for r in recs:
                st.markdown(f"### [{r['title']}]({r['url']})")
                st.markdown(f"*Summary:* {r['summary']}")
                st.markdown(f"*Instructions:*\n\n{r['instructions']}")
                st.markdown("---")
        else:
            st.warning("No recipes found.")

else:
    st.info("Upload an image to begin analysis.")