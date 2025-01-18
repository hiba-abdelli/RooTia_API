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



