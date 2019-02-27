from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode
import logging
import logging.config
from stock.globalvar import *

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
TIMEOUT = 10

class RequestError(Exception):
    pass

def send_request(url, data=None):
    headers = {'User-Agent': USER_AGENT}
    req = Request(url, headers=headers)
    i = 0
    while i < 5:
        try:
            response = None
            if data:
                params = urlencode(data)
                response = urlopen(req, params, timeout=TIMEOUT)
            else:
                response = urlopen(req, timeout=TIMEOUT)

            if response.code != 200:
                raise RequestError('HTTP code is not 200. Error sending request to url: ' + url)
            return response.read()
        except URLError as e:
            logger.error("Request failed for %s with reason: %s" % (url, e.reason))
        except RequestError as e:
            logger.error("Request failed for %s with reason: %s" % (url, e.reason))
        except Exception as e:
            print(str(e))
            logger.error("Unknown error")
        i = i + 1

def download_file(url, path):
    headers = {'User-Agent': USER_AGENT}
    req = urllib2.Request(url, headers=headers)
    i = 0
    while i < 5:
        try:
            response = urlopen(req, timeout=TIMEOUT)
            if response.code != 200:
                raise RequestError('HTTP code is not 200. Error downloading file from url: ' + url)
            content = response.read()
            file = open(path, 'w')
            file.write(content)
            file.close()
            return content
        except URLError as e:
            print("Request failed for %s with reason: %s" % (url, e.reason))
        except RequestError as e:
            print("Request failed for %s with reason: %s" % (url, e.reason))
        except Exception as e:
            print(str(e))
            print("Unknown error")
        i = i + 1

