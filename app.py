import streamlit as st
import pandas as pd
import numpy as np
import base64
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DATABASE_CONFIG
from models import Book, Review
import summarization
from recommendation_model import define_model, recommend_books

# Load the recommendation model
knn, label_encoder, df, scaler = define_model()
# Load the recommendation model
knn, label_encoder, df, scaler = define_model()

# Database setup
DATABASE_URL = (
    f"postgresql+psycopg2://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@"
    f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Authentication
def authenticate(username, password):
    return username == "l" and password == "p"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string


def add_bg_image():
    # Load and encode the image to base64
    image_path = "library.jpg"
    encoded_image = encode_image(image_path)
    
    # Embed CSS for the background image and text areas
    # st.markdown(
    #     f"""
    #     <style>
    #     .stApp {{
    #         background-image: url(data:image/jpeg;base64,{encoded_image});
    #         background-size: cover;
    #         background-position: center;
    #         background-repeat: no-repeat;
    #     }}
    #     .stMarkdown, .stTextInput, .stNumberInput, .stTextArea, .stSlider, .stButton {{
    #         background-color: rgba(255, 255, 255, 0.8);
    #         padding: 10px;
    #         border-radius: 5px;
    #     }}
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )
# Librarian Page
def librarian_page():
    add_bg_image()
    st.title("Librarian Page")

    # Check if the user is already logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
    else:
        # Book Upload and Input Form
        st.header("Add New Book")
        
        book_file = st.file_uploader("Upload Book PDF", type=["pdf"])
        book_url = st.text_input("Or enter URL of the book")
        
        book_id = st.text_input("Book ID")
        book_title = st.text_input("Book Title")
        book_author = st.text_input("Author")
        book_genre = st.text_input("Genre")
        book_year_published = st.number_input("Year Published", min_value=0, max_value=2100, step=1)
        
        if st.button("Save Book"):
            session = Session()
            try:
                # Save book details
                new_book = Book(
                    id=book_id,
                    title=book_title,
                    author=book_author,
                    genre=book_genre,
                    year_published=book_year_published,
                )
                session.add(new_book)
                session.commit()

                # Invoke summarization script
                if book_file:
                    summary = summarization.process_uploaded_book(book_file)
                elif book_url:
                    summary = summarization.process_book_from_url(book_url)
                else:
                    summary = "No summary available"

                # Update book summary
                new_book.summary = summary
                session.commit()
                st.success(f"Book '{book_title}' added successfully!")
            except Exception as e:
                session.rollback()
                st.error(f"Error adding book: {str(e)}")
            finally:
                session.close()
        
        # Display Books Table
        st.header("Books Table")
        session = Session()
        books = session.query(Book).all()
        for book in books:
            st.write(f"ID: {book.id}, Title: {book.title}, Author: {book.author}, Genre: {book.genre}, Year: {book.year_published}")
        session.close()

def recommendation_page():
    add_bg_image()
    st.title("Book Recommendation")

    genre = st.text_input("Enter Genre for Recommendation")

    if st.button("Get Recommendations"):
        if genre:
            session = Session()
            
            # Search for books with the specified genre
            matching_books = session.query(Book, Review).filter(
                Book.genre.ilike(f"%{genre}%"),
                Book.id == Review.book_id
            ).all()
            
            session.close()

            if matching_books:
                book_details = [
                    {
                        'Book ID': book.Book.id,
                        'Title': book.Book.title,
                        'Rating': book.Review.rating,
                        'Genre': book.Book.genre,
                        'Author': book.Book.author,
                        'Year Published': book.Book.year_published,
                        'Summary': book.Book.summary
                    }
                    for book in matching_books
                ]

                st.write(pd.DataFrame(book_details))
            else:
                st.write("No books found for the given genre.")
        else:
            st.error("Please enter a genre.")

# User Page
def user_page():
    add_bg_image()
    st.title("User Page")

    # Display available books
    st.header("Available Books")
    session = Session()
    books = session.query(Book).all()
    st.write(pd.DataFrame({
        'ID': [book.id for book in books],
        'Title': [book.title for book in books],
        'Author': [book.author for book in books],
        'Genre': [book.genre for book in books],
        'Year Published': [book.year_published for book in books],
        'Summary': [book.summary for book in books]
    }))
    session.close()

    # Allow users to submit a review
    st.header("Submit a Review")
    book_id = st.text_input("Enter Book ID")
    user_id = st.text_input("Enter Your User ID")
    review_text = st.text_area("Enter your review")
    rating = st.slider("Rating", 1, 5, 1)

    if st.button("Submit Review"):
        session = Session()
        try:
            new_review = Review(
                book_id=book_id,
                user_id=user_id,
                review_text=review_text,
                rating=rating
            )
            session.add(new_review)
            session.commit()
            st.success("Review submitted successfully!")
        except Exception as e:
            session.rollback()
            st.error(f"Error submitting review: {str(e)}")
        finally:
            session.close()

# Main function
def main():
    st.sidebar.title("Intelligent Book Management System")
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ("Librarian Page", "Recommendation", "User Page"))

    # Check query parameters to see if user is logged in
    query_params = st.query_params
    if query_params.get("logged_in") == ["true"]:
        st.session_state.logged_in = True

    if page == "Librarian Page":
        librarian_page()
    elif page == "Recommendation":
        recommendation_page()
    elif page == "User Page":
        user_page()


if __name__ == "__main__":
    main()