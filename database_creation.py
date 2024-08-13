from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import DATABASE_CONFIG  # Import the configuration
import random

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the Books table
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    year_published = Column(Integer)
    summary = Column(Text)

    # Relationship with the reviews table
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")


# Define the Reviews table
class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)
    review_text = Column(Text)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)

    # Relationship with the books table
    book = relationship("Book", back_populates="reviews")

# Construct the database URL from the configuration
DATABASE_URL = (
    f"postgresql+psycopg2://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@"
    f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Set up the database connection
engine = create_engine(DATABASE_URL)

# Create the tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Sample data for books
sample_books = [
    {"title": "Book Title 1", "author": "Author 1", "genre": "Genre A", "year_published": 2020, "summary": "Summary of Book 1"},
    {"title": "Book Title 2", "author": "Author 2", "genre": "Genre B", "year_published": 2021, "summary": "Summary of Book 2"},
    {"title": "Book Title 3", "author": "Author 3", "genre": "Genre C", "year_published": 2022, "summary": "Summary of Book 3"},
    {"title": "Book Title 4", "author": "Author 4", "genre": "Genre D", "year_published": 2023, "summary": "Summary of Book 4"},
    {"title": "Book Title 5", "author": "Author 5", "genre": "Genre E", "year_published": 2024, "summary": "Summary of Book 5"},
    {"title": "Book Title 6", "author": "Author 6", "genre": "Genre F", "year_published": 2020, "summary": "Summary of Book 6"},
    {"title": "Book Title 7", "author": "Author 7", "genre": "Genre G", "year_published": 2021, "summary": "Summary of Book 7"},
    {"title": "Book Title 8", "author": "Author 8", "genre": "Genre H", "year_published": 2022, "summary": "Summary of Book 8"},
    {"title": "Book Title 9", "author": "Author 9", "genre": "Genre I", "year_published": 2023, "summary": "Summary of Book 9"},
    {"title": "Book Title 10", "author": "Author 10", "genre": "Genre J", "year_published": 2024, "summary": "Summary of Book 10"}
]

# Insert sample books into the database
for book_data in sample_books:
    book = Book(**book_data)
    session.add(book)

session.commit()

# Generate and insert sample reviews for each book
for book in session.query(Book).all():
    for user_id in range(1, 4):  # Add 3 reviews per book
        review = Review(
            book_id=book.id,
            user_id=user_id,
            review_text=f"Review by user {user_id} for {book.title}",
            rating=random.randint(1, 5)
        )
        session.add(review)

session.commit()

print("Sample books and reviews inserted successfully.")

# Close the session
session.close()
