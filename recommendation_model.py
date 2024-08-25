import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt

def define_model():
    # Generate Synthetic Dataset
    np.random.seed(42)

    genres = ['Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 'Biography','history']

    data = {
        'book_id': range(1, 101),
        'title': [f'Book {i}' for i in range(1, 101)],
        'genre': np.random.choice(genres, 100),
        'average_rating': np.random.uniform(1, 5, 100)
    }

    df = pd.DataFrame(data)

    # Data Preprocessing
    label_encoder = LabelEncoder()
    df['genre_encoded'] = label_encoder.fit_transform(df['genre'])

    X = df[['genre_encoded', 'average_rating']]
    y = df['average_rating']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Model Training (K-Nearest Neighbors Regressor)
    knn = KNeighborsRegressor(n_neighbors=5)
    knn.fit(X_train, y_train)

    # Model Evaluation
    y_pred = knn.predict(X_test)

    rmse = sqrt(mean_squared_error(y_test, y_pred))
    print(f'Root Mean Squared Error (RMSE): {rmse}')

    return knn, label_encoder, df, scaler

def recommend_books(model, label_encoder, df, scaler, genre, n_recommendations=5):
    # Handle unseen genre labels
    if genre not in label_encoder.classes_:
        return pd.DataFrame(columns=['book_id', 'title', 'genre', 'average_rating'])

    # Encode the genre
    genre_encoded = label_encoder.transform([genre])[0]
    
    # Create features for the given genre
    avg_rating = np.mean(df[df['genre'] == genre]['average_rating'])
    features = np.array([[genre_encoded, avg_rating]])
    features = scaler.transform(features)
    
    # Get distances and indices of the nearest neighbors
    distances, indices = model.kneighbors(features, n_neighbors=n_recommendations)
    
    # Filter books that belong to the specified genre
    genre_books = df[df['genre'] == genre]
    
    # Add distances as a column to the genre_books dataframe for sorting
    genre_books = genre_books.reset_index()
    genre_books['distance'] = np.nan
    for i, idx in enumerate(indices[0]):
        genre_books.loc[genre_books.index == idx, 'distance'] = distances[0][i]
    
    # Sort by rating (highest first) and by distance (closest first)
    genre_books_sorted = genre_books.sort_values(by=['average_rating', 'distance'], ascending=[False, True])
    
    # Return the top n_recommendations
    recommendations = genre_books_sorted[['book_id', 'title', 'genre', 'average_rating']].head(n_recommendations)
    return recommendations
