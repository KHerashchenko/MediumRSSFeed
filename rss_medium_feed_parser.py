import feedparser
from kafka import KafkaProducer
import time
from datetime import datetime, timedelta
import json
import argparse

# Define and parse the command-line arguments
parser = argparse.ArgumentParser()

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'

# Initialize the Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)


def send_to_kafka(item, topic):
    item_json = json.dumps(item)
    item_bytes = item_json.encode('utf-8')
    # Send the item to the Kafka topic
    producer.send(topic, value=item_bytes)
    producer.flush()


def fetch_and_send_rss_feed(feed_url, date_format, last_event_pubdate, topic, tag):
    # Fetch the RSS feed
    feed = feedparser.parse(feed_url)

    # Check if the feed was fetched successfully
    if feed.bozo:
        print(f"Error fetching RSS feed: {feed.bozo_exception}")
        return

    new_event_pubdate = datetime.strptime(feed.entries[0].published, date_format)
    
    # Process new items
    for entry in feed.entries:
        item = {
            'title': entry.title,
            'link': entry.link,
            'description': entry.description,
            'published': entry.published,
            'tag': tag
        }

        item_pubdate = datetime.strptime(item['published'], date_format)
        if item_pubdate > last_event_pubdate:
            # Send the item to Kafka (you may want to add more processing logic here)
            send_to_kafka(item, topic)
            print('Event sent:')
            print(item)
        else:
            break
    
    return new_event_pubdate


if __name__ == '__main__':
    parser.add_argument('--tag', type=str, help='Medium feed tag', default='data-engineering')
    parser.add_argument('--topic', type=str, help='Kafka topic', default='general')
    parser.add_argument('--sleep', type=int, help='Sleep between pokes (sec)', default=60)
    args = parser.parse_args()

    # RSS feed URL to fetch
    RSS_FEED_URL = f'https://medium.com/feed/tag/{args.tag}'

    # Starting parsing from current date midnight
    DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"
    last_event_pubdate = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    while True:
        # Fetch and send the RSS feed
        last_event_pubdate = fetch_and_send_rss_feed(RSS_FEED_URL, DATE_FORMAT, last_event_pubdate, args.topic, args.tag)

        # Sleep for a specified interval (e.g., 60 seconds)
        time.sleep(args.sleep)
