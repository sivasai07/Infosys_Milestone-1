# E-Commerce Recommendation Engine (Hybrid Approach)

## Project Overview
This project implements an AI-based Hybrid Recommendation Engine for an e-commerce platform. The system recommends products using three different recommendation strategies: Content-Based Filtering, Collaborative Filtering, and Rating / Popularity-Based Recommendation. These models help improve recommendation accuracy and handle scenarios such as new users, similar product suggestions, and popularity-based recommendations.

## Milestone 1: Data Collection & Preprocessing
The first milestone focused on preparing the dataset and building the foundation required for recommendation models.

### Completed Tasks
- Dataset selection from Kaggle for an e-commerce recommendation system
- Data cleaning and preprocessing
- Handling missing values and invalid entries
- Removing invalid User IDs and Product IDs
- Cleaning product image links and text fields
- Exploratory Data Analysis (EDA)
- Creating the User–Item Interaction Matrix
- Preparing the dataset for recommendation models

### Technologies Used
- Python
- Pandas
- NumPy
- Scikit-learn

## Milestone 2: Recommendation Models Implementation
In Milestone 2, three recommendation approaches were implemented to form a hybrid recommendation system.

### 1. Content-Based Recommendation
Content-based filtering recommends products that are similar to the selected product based on product information.

Method:
- Combine product features such as Category, Brand, Description, and Tags
- Convert text data into numerical vectors using TF-IDF
- Compute similarity between products using Cosine Similarity
- Recommend the top similar products

File:
content_based.py

### 2. Collaborative Filtering
Collaborative filtering recommends products based on user behavior and rating patterns.

Method:
- Create a User–Item Matrix from user ratings
- Calculate similarity between items using Cosine Similarity
- Recommend products that are similar based on user interactions

File:
collaborative_based.py

### 3. Rating-Based Recommendation
This model recommends top-rated and popular products.

Method:
- Use a weighted rating formula to balance product rating and review count
- Use popularity-based ranking as a fallback model

File:
rating_based.py

## Project Structure
```text
Infosys_Milestone-1/
│
├── content_based.py
├── collaborative_based.py
├── rating_based.py
├── cleaning_data.py
│
├── requirements.txt
│
└── data/
    └── clean_data.csv
```
## Outcome
By the end of Milestone 2, the project successfully implements three recommendation models: Content-Based Filtering, Collaborative Filtering, and Rating-Based Recommendation. These models together form the core components of a Hybrid AI Recommendation Engine for an e-commerce platform.
