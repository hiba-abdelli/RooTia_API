from extensions import db, bcrypt
from datetime import datetime



class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    chronic_disease = db.Column(db.String(100))
    since_when = db.Column(db.String(100))
    consulting_doctor = db.Column(db.Boolean)
    taking_medication = db.Column(db.Boolean)
    reason_for_herbal_medicine = db.Column(db.String(200))
    

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        } 


    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    business_description = db.Column(db.String(500), nullable=False)
    business_address = db.Column(db.String(200), nullable=False)
    business_website = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)  
    social_media_links = db.Column(db.JSON, nullable=True)  

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('businesses', lazy=True))
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# herbs_tables

class Herb(db.Model):
    __tablename__ = 'herbs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(100), nullable=True)
    family = db.Column(db.String(100), nullable=True)
    region_found = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    traditional_use = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    uses = db.relationship('Use', backref='herb', lazy=True)
    risks = db.relationship('Risk', backref='herb', lazy=True)
    diseases = db.relationship('Disease', secondary='herb_disease', backref=db.backref('herbs', lazy=True))


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }



class Use(db.Model):
    __tablename__ = 'uses'
    
    id = db.Column(db.Integer, primary_key=True)
    herb_id = db.Column(db.Integer, db.ForeignKey('herbs.id'), nullable=False)
    use_description = db.Column(db.Text, nullable=False)  # Description of the use
    dosage = db.Column(db.String(100), nullable=True)  # Optional dosage information

class Risk(db.Model):
    __tablename__ = 'risks'
    
    id = db.Column(db.Integer, primary_key=True)
    herb_id = db.Column(db.Integer, db.ForeignKey('herbs.id'), nullable=False)
    risk_description = db.Column(db.Text, nullable=False)  # Description of the risk
    affected_groups = db.Column(db.String(100), nullable=True)  # Optional affected groups

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the disease
    description = db.Column(db.Text, nullable=True)  # Description of the disease
    common_treatments = db.Column(db.Text, nullable=True)  # Common treatments for the disease

class HerbDisease(db.Model):
    __tablename__ = 'herb_disease'
    
    herb_id = db.Column(db.Integer, db.ForeignKey('herbs.id'), primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), primary_key=True)
    
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    herb_id = db.Column(db.Integer, db.ForeignKey('herbs.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating out of 5
    review = db.Column(db.Text, nullable=True)  # Optional textual review
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    herb = db.relationship('Herb', backref=db.backref('herb_reviews', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'herb_id': self.herb_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None,
            'herb': self.herb.to_dict() if self.herb else None
        }


class Ad(db.Model):
    __tablename__ = 'ad'  
    __table_args__ = {'extend_existing': True}  # to Avoid redefinition error

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    media_type = db.Column(db.String(50), nullable=False)  # e.g., 'image', 'video', 'text'
    media_url = db.Column(db.String(500), nullable=True)  # List of media URLs as a  comma-separated string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    business = db.relationship('Business', backref='ads')

    def __init__(self, business_id, title, description, media_type, media_url):
        self.business_id = business_id
        self.title = title
        self.description = description
        self.media_type = media_type
        self.media_url = media_url


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Sender or receiver (user)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=True)  # Sender or receiver (business)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=True)  # Optional: for ad-related conversations
    conversation_id = db.Column(db.Integer, nullable=False)  # New: Conversation ID
    content = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500), nullable=True)  # Optional
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('sent_messages', lazy=True))
    business = db.relationship('Business', backref=db.backref('received_messages', lazy=True))

    def __repr__(self):
        return f"<Message {self.id} (Conversation {self.conversation_id})>"
        
class ResearchArticle(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    pubmed_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    authors = db.Column(db.Text, nullable=True)  # Comma-separated list
    publication_date = db.Column(db.Date)
    article_url = db.Column(db.String(255), nullable=False)
    keywords = db.Column(db.String(255), nullable=True)  # Query or matched keywords
    region = db.Column(db.String(50), nullable=True)  # e.g., 'Tunisia', 'North Africa'

    def to_dict(self):
        return {
            'id': self.id,
            'pubmed_id': self.pubmed_id,
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'article_url': self.article_url,
            'keywords': self.keywords,
            'region': self.region,
        }


class NewsArticle(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    published_at = db.Column(db.DateTime, nullable=False)
    source_name = db.Column(db.String(200), nullable=False)
    keywords = db.Column(db.String(500), nullable=True)  # Increased the size slightly for flexibility
    
    def __repr__(self):
        return f"<NewsArticle {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'url': self.url,
            'published_at': self.published_at,
            'source_name': self.source_name,
            'keywords': self.keywords.split(',') if self.keywords else []
        }
