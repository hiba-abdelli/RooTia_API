import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_default_jwt_secret_key'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql://root:Hibaabdelli19%40@localhost/herbal_medicine')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# OAuth 2.0
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or '152838997088-k5j34u36gv8osrjej8pnkrngg9c85gst.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or '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'
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    OAUTH_REDIRECT_URI = "http://127.0.0.1:5001/auth/oauth-callback"
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs' 

# default keywords for herbal medicine news (for the integration Google NewsAPI)
    HERB_KEYWORDS = os.getenv('HERB_KEYWORDS', 'Tunisian medicinal herbs, North African herbal medicine, Healing herbs Tunisia ,medicinal plants , alternative medecine , natural treatment , herb healing ').split(',')
    
# Google News API key
    GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY', '3cd86a5483c44de4acfa3ddedfc8a6c7')  


    