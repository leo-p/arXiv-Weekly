import os
import json
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Define script variables
SENDER_EMAIL = "arxiv.weekly@gmail.com"
RECEIVER_EMAIL = "leo.paillier@gmail.com"
PAPERS_JSON_FILE = "papers.json"


# Define logger
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(levelname)s %(name)s %(asctime)s %(process)d %(thread)d %(filename)s:%(lineno)s] %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


def open_json_from_file(json_path):
    """Returns JSON content from file path.

    Args:
        json_path (str): JSON file path.

    Returns:
        JSON: JSON content.
    """
    try:
        with open(json_path) as json_file:
            json_data = json.load(json_file)
            return json_data
    except:
        LOGGER.error("Could not open file {} in json format.".format(json_path))


def build_multipart_email(sender_email, receiver_email, papers):
    """Builds a multipart plain-text/HTML MIME email with the top 3 papers.

    Args:
        sender_email (str): Sender email address.
        receiver_email (str): Receiver email address.
        papers (JSON): JSON containing papers data.

    Returns:
        email.mime.multipart.MIMEMultipart: The MIME Multipart email to send.
    """
    # Make sure we have at least 3 papers
    if len(papers) < 3:
        raise ValueError(f"Less than 3 papers present.")

    # Remove unwanted characters in the papers
    for paper in papers:
        paper['title'] = " ".join(paper['title'].split())
        paper['abstract'] = " ".join(paper['abstract'].split())

    # Define subject, sender, and receiver
    message = MIMEMultipart("alternative")
    message["Subject"] = f"arXiv Weekly: {papers[0]['title']} & 2 more"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text version
    text = f"Hi there,\n\nHere are the top 3 arXiv papers this week:\n\n"
    for ii, paper in enumerate(papers[:3]):
        text += f"\t{ii + 1}/ {paper['title']} - {', '.join(paper['authors'])} ({' | '.join(paper['tags'])})\n"
        text += f"\t-> {paper['link']}\n"
        text += f"\t{paper['abstract']}\n\n"
    text += "That's all for the week!\n\n\n"
    text += "Click www.here.com to unsubscribe or contact me directly at leo.paillier@gmail.com"

    # # Create the HTML version
    # html = """\
    # <html>
    # <body>
    #     <p>Hi,<br>
    #     How are you?<br>
    #     <a href="http://www.realpython.com">Real Python</a>
    #     has many great tutorials.
    #     </p>
    # </body>
    # </html>
    # """

    # Add HTML/plain-text parts to MIMEMultipart message
    part1 = MIMEText(text, "plain")
    # part2 = MIMEText(html, "html")
    message.attach(part1)
    # message.attach(part2)

    return message


def send_email(sender_email, receiver_email, message):
    """[summary]

    Args:
        sender_email (str): Sender email address.
        receiver_email (str): Receiver email address.
        message (email.mime.multipart.MIMEMultipart): The MIME Multipart email to send.
    """
    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=context) as server:
        # Retrieve credentials
        gmail_username = os.getenv('GMAIL_USERNAME', default=None)
        gmail_password = os.getenv('GMAIL_PASSWORD', default=None)

        if gmail_username and gmail_password:
            server.login(gmail_username, gmail_password)
            server.sendmail(sender_email, receiver_email, message.as_string())


if __name__ == '__main__':
    # Retrieve papers data
    papers = open_json_from_file(PAPERS_JSON_FILE)

    # Build email
    message = build_multipart_email(SENDER_EMAIL, RECEIVER_EMAIL, papers)

    # Send email
    send_email(SENDER_EMAIL, RECEIVER_EMAIL, message)
