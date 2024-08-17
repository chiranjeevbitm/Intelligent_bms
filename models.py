from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import DATABASE_CONFIG
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

# Define the database URL
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
