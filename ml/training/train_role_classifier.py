"""
ML Role Classification Model Training Script
Trains a TF-IDF vectorizer + Calibrated Logistic Regression classifier on occupational career profiles.
Saves model artifacts to ml/models/
"""

import os
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Training dataset with diverse synthetic/standard profiles for 10 MCA major project roles
TRAINING_DATA = [
    # Python Developer
    ("python developer backend rest api fastapi django flask sql postgresql orm celery redis docker pytest microservices", "Python Developer"),
    ("experienced python engineer building async services with sqlalchemy pydantic fast api and unit testing with pytest", "Python Developer"),
    ("backend developer with django rest framework relational database design mysql query optimization git ci cd", "Python Developer"),
    ("software engineer python flask rest apis git linux docker redis caching background tasks", "Python Developer"),
    
    # Data Scientist
    ("data scientist machine learning pandas numpy scikit-learn statistical modeling regression classification clustering eda python", "Data Scientist"),
    ("predictive modeling feature engineering data science exploratory data analysis seaborn matplotlib jupyter hypothesis testing", "Data Scientist"),
    ("machine learning algorithms random forest xgboost gradient boosting cross validation precision recall python data science", "Data Scientist"),
    ("applied data scientist extracting insights from large datasets using pandas sql statistical methods and scikit learn models", "Data Scientist"),

    # ML Engineer
    ("machine learning engineer deep learning pytorch tensorflow cnn rnn lstm model deployment mlops docker triton onnx", "ML Engineer"),
    ("ml engineer trained neural networks with pytorch deployed real-time inference api using fastapi containerized with docker", "ML Engineer"),
    ("computer vision nlp transformers huggingface object detection yolo deep learning model optimization and serving", "ML Engineer"),
    ("end-to-end machine learning pipeline building data ingestion model training hyperparameter tuning and production deployment", "ML Engineer"),

    # AI Engineer
    ("ai engineer generative ai large language models prompt engineering langchain huggingface rag vector database embeddings", "AI Engineer"),
    ("artificial intelligence developer fine-tuning open source llms building retrieval augmented generation pipelines with faiss", "AI Engineer"),
    ("deep learning ai specialist working with foundation models conversational agents transformers pytorch api integration", "AI Engineer"),

    # Data Analyst
    ("data analyst sql power bi tableau excel business intelligence reporting kpi dashboards data cleaning vlookup dax", "Data Analyst"),
    ("business data analyst writing complex sql queries joins aggregations window functions creating executive power bi visual reports", "Data Analyst"),
    ("tableau dashboard specialist creating interactive visual analytics extracting data with sql analyzing business performance metrics", "Data Analyst"),
    ("financial and operational data analyst excel spreadsheets pivot tables sql database queries data visualization", "Data Analyst"),

    # Full Stack Developer
    ("full stack developer react node.js javascript html5 css3 express rest api mongodb sql responsive design git", "Full Stack Developer"),
    ("frontend backend full stack engineer building responsive web applications using react hooks next.js nodejs express and postgresql", "Full Stack Developer"),
    ("web developer react js single page applications rest api integration tailwind css node js backend database connection", "Full Stack Developer"),
    ("mern stack developer mongodb express react nodejs building modern scalable web portals with jwt authentication", "Full Stack Developer"),

    # Backend Developer
    ("backend developer java spring boot microservices rest api sql postgresql hibernate kafka docker distributed systems", "Backend Developer"),
    ("server-side backend engineer designing high throughput rest apis relational databases indexing transactions and caching", "Backend Developer"),
    ("backend software engineer api security jwt authentication redis caching database schema design linux server maintenance", "Backend Developer"),

    # Database Developer
    ("database developer dba sql mysql postgresql oracle stored procedures indexing triggers normalization performance tuning", "Database Developer"),
    ("database administrator designing relational schemas optimizing complex queries transaction isolation levels backup replication", "Database Developer"),
    ("relational database specialist writing pl sql stored procedures query profiling query execution plan analysis ddl dml", "Database Developer"),

    # Business Analyst
    ("business analyst agile scrum requirements gathering user stories product backlog jira stakeholder management process mapping", "Business Analyst"),
    ("business systems analyst conducting gap analysis defining functional specifications collaborating with engineering teams", "Business Analyst"),
    ("it business analyst workflow optimization business requirements document brd user acceptance testing uat communication", "Business Analyst"),

    # Software Engineer
    ("software engineer c++ java python data structures algorithms object oriented programming design patterns problem solving linux git", "Software Engineer"),
    ("core software developer algorithmic problem solving oop principles multithreading unit testing continuous integration", "Software Engineer"),

    # DevOps / Cloud Engineer
    ("devops engineer aws azure docker kubernetes ci cd github actions terraform linux infrastructure as code monitoring prometheus", "DevOps / Cloud Engineer"),
    ("cloud infrastructure engineer automating container deployment with docker kubernetes managing aws ec2 s3 rds and ci cd pipelines", "DevOps / Cloud Engineer")
]

def train_and_export():
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
        ('clf', LogisticRegression(C=1.0, max_iter=200, class_weight='balanced'))
    ])

    print("Training ML Career Role Classifier...")
    pipeline.fit(texts, labels)

    model_file = MODEL_DIR / "role_classifier.pkl"
    joblib.dump(pipeline, model_file)
    print(f"Model successfully trained and saved to: {model_file}")

if __name__ == "__main__":
    train_and_export()
