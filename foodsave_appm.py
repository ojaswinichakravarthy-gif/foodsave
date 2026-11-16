import streamlit as st
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import numpy as np
import requests
import cv2
import torch
import yolov5

st.set_page_config(page_title="FoodSave - Reduce Food Waste", layout="centered")

# Load the models once
model = MobileNetV2(weights='imagenet')
yolo_model = yolov5.load('yolov5s.pt')

st.title("🍽 FoodSave - AI Recipe Recommender")
st.write("Upload a picture of your leftover or available food items and get recipe suggestions to reduce food waste!")

uploaded_image = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

def predict_ingredients(img):
    img = img.resize((224, 224))
    x = np.array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    decoded = decode_predictions(preds, top=3)[0]
    ingredients = [item[1] for item in decoded]
    return ingredients

def detect_objects(img):
    img_np = np.array(img)
    results = yolo_model(img_np)
    detections = results.pandas().xyxy[0]
    return detections

def get_recipes(ingredients):
    # Placeholder for a real API. You can use Spoonacular, Edamam, etc.
    sample_recipes = {
        'banana': ["Banana Smoothie", "Banana Pancakes"],
        'broccoli': ["Broccoli Stir Fry", "Broccoli Soup"],
        'carrot': ["Carrot Salad", "Carrot Halwa"],
        'cheese': ["Mac and Cheese", "Grilled Cheese Sandwich"],
        'tomato': ["Tomato Soup", "Pasta with Tomato Sauce"]
    }
    suggested = set()
    for item in ingredients:
        for key in sample_recipes:
            if key in item.lower():
                suggested.update(sample_recipes[key])
    return list(suggested) if suggested else ["No matching recipes found. Try uploading a clearer food image."]

if uploaded_image is not None:
    try:
        img = Image.open(uploaded_image)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        
        with st.spinner("Analyzing image and fetching recipes..."):
            # Predict ingredients using MobileNetV2
            ingredients = predict_ingredients(img)
            st.success(f"Identified ingredients: {', '.join(ingredients)}")
            
            # Detect objects using YOLOv5
            detections = detect_objects(img)
            st.subheader("🔍 Object Detection Results:")
            for index, row in detections.iterrows():
                st.write(f"Object: {row['name']}, Confidence: {row['confidence']:.2f}")
            
            # Get recipe suggestions
            recipes = get_recipes(ingredients)
            st.subheader("🍳 Recipe Suggestions:")
            for recipe in recipes:
                st.markdown(f"- {recipe}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload an image to get started.")

# Add a footer
st.markdown("""
<footer style="position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #f1f1f1;">
    <p>© 2023 FoodSave. All rights reserved.</p>
</footer>
""")