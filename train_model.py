import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import resample
import pickle

# Load data
data = pd.read_csv('comments.csv')

# 🔧 Fix 1: Balance the dataset
majority = data[data.sentiment == 'positive']
minority = data[data.sentiment == 'negative']

# 🔁 Upsample or downsample
minority_upsampled = resample(minority,
                               replace=True,
                               n_samples=len(majority),
                               random_state=42)

data_balanced = pd.concat([majority, minority_upsampled])

# Vectorize
X = data_balanced['feedback']
y = data_balanced['sentiment']

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# 🔧 Fix 2: Add class_weight='balanced' just in case
model = RandomForestClassifier(class_weight='balanced')
model.fit(X_vec, y)

# Save it
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(model, open("model.pkl", "wb"))
