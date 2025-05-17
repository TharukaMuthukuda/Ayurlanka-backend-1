import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load your data (CSV with 'feedback' & 'label' columns)
data = pd.read_csv('comments.csv')

X = data['feedback']
y = data['sentiment']

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

model = RandomForestClassifier()
model.fit(X_vec, y)

# Save both vectorizer and model
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(model, open("model.pkl", "wb"))
