import streamlit as st
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string

def add_bg_image():
    # Load and encode the image to base64
    image_path = "library.jpg"
    encoded_image = encode_image(image_path)
    
    # Embed CSS for the background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpeg;base64,{encoded_image});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def main():
    add_bg_image()
    st.title("Test Page")
    st.write("This is a test page with a background image.")

if __name__ == "__main__":
    main()
