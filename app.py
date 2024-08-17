import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DATABASE_CONFIG
from models import Book, Review
import summarization

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

# Librarian Page
def librarian_page():
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
                st.experimental_set_query_params(logged_in="true")  # Update query params to simulate rerun
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

# User Page
def user_page():
    st.title("User Page")

    # Display available books
    st.header("Available Books")
    session = Session()
    books = session.query(Book).all()
    for book in books:
        st.write(f"ID: {book.id}, Title: {book.title}, Author: {book.author}, Genre: {book.genre}, Year: {book.year_published}")
        st.write(f"Summary: {book.summary}")
    
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

# Main Function
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ("Librarian Page", "User Page"))

    # Check query parameters to see if user is logged in
    query_params = st.experimental_get_query_params()
    if query_params.get("logged_in") == ["true"]:
        st.session_state.logged_in = True

    if page == "Librarian Page":
        librarian_page()
    elif page == "User Page":
        user_page()

if __name__ == "__main__":
    main()
