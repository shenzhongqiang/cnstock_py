import urllib
import urllib2

def send_request(url):
    user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req, timeout=10)
    return response.read()
