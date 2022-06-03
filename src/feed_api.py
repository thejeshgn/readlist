import requests
import base64
import json
import logging
import trafilatura
import pytz


class Api:
    DB_API = None
    auth = None
    do_debug = False
    requests_session = None
    author = {}
    home_page_url = ""
    version = "https://jsonfeed.org/version/1.1"
    feed_base_url = ""

    def __init__(
        self,
        couchdb_url,
        user,
        pwd,
        author,
        home_page_url,
        feed_base_url,
        ignore_ssl_errors=False,
        debug=False,
    ):
        auth = user + ":" + pwd
        self.auth = "Basic " + base64.b64encode(auth.encode("utf-8")).decode("utf-8")
        self.requests_session = requests.Session()
        self.do_debug = debug
        self.author = author
        self.home_page_url = home_page_url
        self.feed_base_url = feed_base_url
        if debug:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        if ignore_ssl_errors:
            from urllib3.exceptions import InsecureRequestWarning

            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            self.requests_session.verify = False
        self.DB_API = couchdb_url

    """
    Create a new channel.
    """

    def create_new_channel(self, channel_id, title=None, description=None):
        channel = {
            "type": "channel",
            "_id": channel_id,
            "title": title,
            "description": description,
            "version": self.version,
            "feed_url":self.feed_base_url.format(channel_id),
            "home_page_url": self.home_page_url,
            "type": "channel",
            "author": self.author,
            "authors": [self.author],
            "items" :[]
        }
        r = self.requests_session.put(
            self.DB_API + "/" + requests.utils.quote(channel_id, safe=""),
            json.dumps(channel),
            headers={"Authorization": self.auth},
        )
        if r.status_code in [200, 201]:
            pass
        else:
            raise Exception("DB server error: {}".format(r.status_code))

    """
    Create a new item.
    """

    def upsert_new_item(self, channel_id, new_item):
        print(new_item)
        self.debug("updating program blacklist")
        r = self.requests_session.get(
            self.DB_API + "/" + requests.utils.quote(channel_id, safe=""),
            headers={"Authorization": self.auth},
        )

        if r.status_code != 200:
            raise Exception("DB server error: {}".format(r.status_code))
        channel = r.json()
        items = channel["items"]
        new_items = list(filter(lambda d: d["id"] != new_item["id"], items))
        new_items.append(new_item)
        channel["items"] = new_items
        r = self.requests_session.put(
            self.DB_API + "/" + requests.utils.quote(channel_id, safe=""),
            json.dumps(channel),
            headers={"Authorization": self.auth},
        )
        if r.status_code in [200, 201]:
            pass
        else:
            raise Exception("DB server error: {}".format(r.status_code))

    """
    Create a new item.
    """

    def scrape_document(self, url, include_full_content=False):
        downloaded = trafilatura.fetch_url(url)
        output = trafilatura.extract(
            downloaded,
            include_formatting=True,
            include_links=True,
            include_images=True,
            include_tables=True,
            output_format="json",
        )
        data = json.loads(output)
        print(data)
        item = {}
        item["type"] = "item"
        item["id"] = url
        item["url"] = url
        item["external_url"] = url
        item["title"] = data["title"]
        if "date" in data:
            item_date = str(data["date"])
            if len(item_date) < 11:
                item_date = item_date + "T00:00:00+05:30"            
            item["date_published"] = item_date
            item["date_modified"] = item_date
        else:
            item["date_published"] = get_datetime()
            item["date_modified"] = get_datetime()

        # Pick author if not pick domain as author
        if "author" in data and data["author"]:
            item["author"] = {"name": data["author"]}
            item["authors"] = [{"name": data["author"]}]
        else:
            item["author"] = {"name": data["hostname"]}
            item["authors"] = [{"name": data["hostname"]}]

        if "lead_image_url" in data and data["lead_image_url"]:
            item["image"] = data["lead_image_url"]

        item["summary"] = data["excerpt"]
        if include_full_content:
            item["content_html"] = data["raw_text"]
        else:
            item["content_html"] = data["excerpt"]
        return item

    def debug(self, msg):
        if self.do_debug:
            print("[DEBUG] " + msg)

    def get_datetime():
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.datetime.now(tz).isoformat()
        return str(now)
