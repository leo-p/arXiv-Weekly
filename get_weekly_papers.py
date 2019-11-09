import json
import logging
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


# Define script variables
ARXIV_WEEKLY_URL = "http://www.arxiv-sanity.com/top?timefilter=week&vfilter=all"
PAPERS_JSON_FILE = "papers.json"


# Define logger
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(levelname)s %(name)s %(asctime)s %(process)d %(thread)d %(filename)s:%(lineno)s] %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


def save_json_to_file(json_data, json_path):
    """Saves a JSON dictionnary to file.

    Args:
        json_data (JSON): JSON payload to save.
        json_path (str): File path.
    """
    try:
        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file)
        LOGGER.info("JSON saved to file {}".format(json_path))
    except:
        LOGGER.error("Could not save file {} in json format.".format(json_path))
        raise


def is_good_html_response(resp):
    """Returns True if the response seems to be HTML, False otherwise.

    Args:
        resp (requests.models.Response): URL response from requests.

    Returns:
        bool: Whether the response is HTML or not.
    """
    content_type = resp.headers['Content-Type'].lower()
    return resp.status_code == 200 and content_type is not None and content_type.find('html') > -1


def get_url(url):
    """Retrieves HTML payload of an URL.

    Args:
        url (str): URL to fetch.

    Returns:
        str: URL HTML content or None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_html_response(resp):
                LOGGER.info(f"Retrieved URL content for {url}")
                return resp.content
            else:
                raise ValueError(f"URL {url} is a not valid HTML response.")
    except RequestException as e:
        LOGGER.error(f"Error during requests to {url} : {str(e)}")
        raise


def get_papers_from_url(url):
    """Extracts paper data as JSON from URL source code.

    Args:
        url (str): URL to fetch.

    Returns:
        JSON: All papers data.
    """
    # Retrieve HTML content
    html_content = BeautifulSoup(get_url(url), 'html.parser')

    # Find specific papers var from source code
    papers_script = html_content.find_all('script')[-1]
    for line in str(papers_script).splitlines():
        if line.startswith('var papers ='):
            # Remove 'var papers = ' from beggining and ';' from ending
            return json.loads(line[13:-1])
    else:
        raise ValueError('Papers list not found in HTML source.')


if __name__ == '__main__':
    # Download papers data from arXiv Sanity then store it to JSON
    papers = get_papers_from_url(ARXIV_WEEKLY_URL)
    save_json_to_file(papers, PAPERS_JSON_FILE)
