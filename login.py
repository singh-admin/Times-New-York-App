from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import requests
import json

app = Flask(__name__)
CORS(app)

DB_NAME = 'user'
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = '5432'


conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cur = conn.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS user_utility (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        searches JSONB
    )
""")
conn.commit()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cur.execute("SELECT user_id FROM user_utility WHERE username=%s", (username,))
    existing_user = cur.fetchone()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("INSERT INTO user_utility (username, password) VALUES (%s, %s) RETURNING user_id", (username, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'message': 'User created successfully', 'user_id': user_id})
    except Exception as e:
        print(e, "error")
        return jsonify({'message': 'User created successfully', 'user_id': user_id})

NYT_API_KEY = 'Z7TM2AhX24Qz0YT6t1fxs4dGN6rVCwzq'

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q')
    user_id = request.args.get('user_id')

    article_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q={search_term}&api-key={NYT_API_KEY}"
    article_response = requests.get(article_url)
    print(article_response, "###########")
    article_results = article_response.json()
    print(article_results)

    # Search books using New York Times Books API
    books_url = f"https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json?title={search_term}&api-key={NYT_API_KEY}"
    books_response = requests.get(books_url)
    books_results = books_response.json()

    if article_response.status_code == 200 and article_results.get('response', {}).get('docs', []):
        limited_articles = []
        for article in article_results.get('response', {}).get('docs', []):
            limited_articles.append({
                'headline': article.get('headline', {}).get('main'),
                'abstract': article.get('abstract'),
                'pub_date': article.get('pub_date'),
            })
    else:
        search_results = {'message': 'No articles found for this search term.'}

    # Combine article and book results
    search_results = {
        'articles': article_results,
        'books': books_results
    }


    cur.execute("UPDATE user_utility SET searches = %s WHERE user_id = %s", (json.dumps(limited_articles), user_id))
    conn.commit()
    return jsonify(search_results)

if __name__ == '__main__':
    app.run(debug=True)
