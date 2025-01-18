import requests
from models import Herb, ResearchArticle , NewsArticle
from datetime import datetime
from flask import Blueprint, request, render_template
from extensions import db
from dateutil import parser
from flask import jsonify
from flask import current_app


# Create a Blueprint for external routes
external = Blueprint('external', __name__)


###### Integration of PubMed API 

# Function to fetch PubMed IDs (esearch.fcgi)
def fetch_pubmed_ids(query):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 100  # Maximum articles to fetch
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    else:
        raise Exception(f"Error fetching PubMed IDs: {response.status_code}")

# Function to fetch PubMed summaries (esummary.fcgi)
def fetch_pubmed_summaries(pubmed_ids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "json"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json().get("result", {})
        # Exclude "uids" key, which isn't an article
        data.pop("uids", None)
        return data
    else:
        raise Exception(f"Error fetching PubMed summaries: {response.status_code}")

# Function to save articles to the database
def save_article_to_db(article_data):
    # Check if the article already exists
    existing_article = ResearchArticle.query.filter_by(pubmed_id=article_data['pubmed_id']).first()
    if existing_article:
        print(f"Article with PubMed ID {article_data['pubmed_id']} already exists.")
        return
    # Debug: print authors to check the format
    print("Authors:", article_data['authors'])

    # Create a new article entry
    publication_date = None
    if article_data.get('publication_date'):
        try:
            publication_date = parser.parse(article_data['publication_date'])
        except ValueError:
            # Handle different date formats here
            publication_date = None  # or log an error

    article = ResearchArticle(
        pubmed_id=article_data['pubmed_id'],
        title=article_data['title'],
        abstract=article_data.get('abstract'),
        authors=', '.join(article_data['authors']),
        publication_date=publication_date,
        article_url=article_data['article_url'],
        keywords=article_data.get('keywords')
    )
    
    # Save to the database
    db.session.add(article)
    db.session.commit()
    print(f"Article '{article.title}' saved to database.")

# Function to fetch and store articles with tailored filters
def fetch_and_store_articles():
    # Queries related to Tunisian herbs and medicinal context
    queries = [
        "Tunisian medicinal herbs",
        "North African herbal medicine",
        "medicinal plants from Tunisia",
        "Herbs for diabetes Tunisia",
        "Herbs for thyroid Tunisia",
        "medicinal herbs in Tunisia",
        "healing tunisian plants  "
    ]
    
    # Fetch herb names from the database
    herbs = [herb.name.lower() for herb in Herb.query.all()]
    
    for query in queries:
        article_ids = fetch_pubmed_ids(query)
        summaries = fetch_pubmed_summaries(article_ids)
        
        for pmid, article in summaries.items():
            title = article['title'].lower()
            abstract = article.get('summary', '').lower()
            
            # Debug: Check the structure of authors
            print(f"Processing article {pmid}")
            print("Authors field:", article.get('authors', []))  # Debug: print authors field
            
            # Extract authors safely
            authors = []
            if isinstance(article.get('authors', []), list):
                authors = [
                    author.get('name', '') if isinstance(author, dict) else str(author)
                    for author in article['authors']
                ]
            
            # Check for relevance based on herbs and context
            if (
                any(herb in title or herb in abstract for herb in herbs) or
                "tunisia" in title or "north africa" in title
            ) and article.get('pubdate', '') > '2018-01-01':
                # Extract author names from the author dictionaries
                authors = [
                    author.get('name', '') if isinstance(author, dict) else str(author)
                    for author in article.get('authors', [])
                ]
                article_data = {
                    'pubmed_id': pmid,
                    'title': article['title'],
                    'abstract': article.get('summary', 'No abstract available'),
                    'authors': authors,
                    'publication_date': article.get('pubdate', None),
                    'article_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'keywords': query,
                }
                save_article_to_db(article_data)


# Test route for fetching and storing articles
@external.route('/test-fetch-articles', methods=['POST'])
def test_fetch_articles():
    try:
        fetch_and_store_articles()
        return {"message": "Articles fetched and stored successfully!"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# Route to display articles from the database

@external.route('/research-articles')
def research_articles():
    try:
        # Get the query parameter from the request
        query = request.args.get('query')  # Optional filtering by keyword
        
        # Check if query is provided and filter accordingly
        if query:
            print(f"Filtering articles with query: {query}")  # Debug: print the query
            articles = ResearchArticle.query.filter(ResearchArticle.keywords.ilike(f"%{query}%")).all()
        else:
            articles = ResearchArticle.query.all()  # Return all articles if no query is provided

        # Log the number of articles fetched
        print(f"Number of articles fetched: {len(articles)}")

        # If no articles found, raise an error
        if not articles:
            raise ValueError("No articles found matching the query.")

        # Convert articles to dictionary format
        articles_data = [article.to_dict() for article in articles]
        print(f"Articles data: {articles_data}")  # Debug: print the data before sending the response

        # Return the articles as a JSON response for easier testing in Postman
        return {"articles": articles_data}, 200

    except ValueError as ve:
        # Handle cases where no articles are found
        print(f"ValueError: {str(ve)}")  # Log the error
        return {"error": str(ve)}, 404  # Return a 404 error with the message

    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected Error: {str(e)}")  # Log the error
        return {"error": "An unexpected error occurred. Please try again later."}, 500


###### Integration of Google NewsAPI 

NEWS_API_KEY = "3cd86a5483c44de4acfa3ddedfc8a6c7" # the key i got after registering in Google NewsAPI 

def fetch_news_articles(keywords):
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": keywords,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 100,  # Fetch up to 100 articles
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for article in articles:
            save_news_article_to_db(article, keywords)
    else:
        raise Exception(f"Error fetching news articles: {response.status_code} - {response.text}")

def save_news_article_to_db(article_data, keywords):
    # Check if the article already exists
    existing_article = NewsArticle.query.filter_by(url=article_data['url']).first()
    if existing_article:
        print(f"Article '{article_data['title']}' already exists.")
        return

    # Create a new article entry
    article = NewsArticle(
        title=article_data['title'],
        description=article_data.get('description'),
        content=article_data.get('content'),
        url=article_data['url'],
        published_at=datetime.strptime(article_data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
        source_name=article_data['source']['name'],
        keywords=keywords
    )
    db.session.add(article)
    db.session.commit()
    print(f"Article '{article.title}' saved to database.")

# Fetch news endpoint
@external.route('/fetch-news', methods=['POST'])
def fetch_news():
    try:
        keywords = request.json.get('keywords', ", ".join(current_app.config['HERB_KEYWORDS']))  # Use default keywords from config
        fetch_news_articles(keywords)
        return jsonify({"message": "News articles fetched and stored successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Display news articles endpoint
@external.route('/news-articles', methods=['GET'])
def get_news_articles():
    query = request.args.get('query')  # Optional filtering by keyword
    if query:
        articles = NewsArticle.query.filter(NewsArticle.keywords.ilike(f"%{query}%")).all()
    else:
        articles = NewsArticle.query.all()

    articles_data = [{
        "title": article.title,
        "description": article.description,
        "content": article.content,
        "url": article.url,
        "published_at": article.published_at.isoformat(),
        "source_name": article.source_name,
        "keywords": article.keywords.split(',') if article.keywords else []
    } for article in articles]

    return jsonify(articles_data), 200