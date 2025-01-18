from app import create_app
from extensions import socketio 
from apscheduler.schedulers.background import BackgroundScheduler


#Define the job to fetch articles
def fetch_articles_job():
    from routes.external import fetch_and_store_articles
    print("Scheduled task: Fetching articles from PubMed...")
    fetch_and_store_articles("Tunisian herbal medicine")
    print("Scheduled task complete!")


app = create_app()

# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_articles_job, 'interval', days=7)  # Fetch every 7 days 
scheduler.start()

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "fetch_articles":
        print("Manual task: Fetching articles from PubMed...")
        fetch_and_store_articles("Tunisian herbal medicine")
        print("Manual task complete!")
    else:
        print("Starting main server with scheduled tasks...")
        socketio.run(app, debug=True, port=5001)

    #print("Starting main server...")
    #socketio.run(app, debug=True , port=5001)  # Start the SocketIO server



## the choice was made in the first place for organization, flexibility, and maintainability,
#This starts both the Flask app and WebSocket server.
#Necessary for real-time features like chat, live notifications, 
# or room-based events.
#The app will behave the same as when running app.py 
# but with added WebSocket functionality.

#I created main.py to handle specific requirements 
# for running a SocketIO server alongside my regular 
# Flask application.
#It allows me to isolate the logic for handling 
# WebSocket connections, real-time features, and 
# the server configuration, while keeping app.py 
# clean and focused on initializing the core Flask app and routes.
# This separation provides more flexibility for managing 
# services and makes it easier to scale or adjust 
# specific parts of the application, such as 
# real-time communication, without affecting the main application logic." 