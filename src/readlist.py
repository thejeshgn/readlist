#!/usr/bin/python3

"""Readlist Client

Usage:
  readlist get
  readlist use <channel>
  readlist new -c <channel> -t <title> -d <description>
  readlist [-c <channel>] [-f] add <url> 

Options:
  -h --help            Show this screen.
  -v --version         Version of this program
  -c <channel>         Select a channel to limit the command to. Not required when the command "use" has been run before.
"""

import os
import sys
import json
import re
from . import feed_api
from urllib.parse import urlparse
from docopt import docopt

CONFIG_FILE = "~/.readlist/config.json"
VERSION = "0.7"


class ReadlistClient:
    config = {}
    file_config = None
    arguments = None
    api = None

    def __init__(self, arguments, config=None):
        if not str(type(arguments)) == "<class 'docopt.Dict'>":
            self.arguments = docopt(__doc__, argv=arguments, version=VERSION)
        else:
            self.arguments = arguments

        if not config:
            self.load_config()
            self.file_config = True
        else:
            self.config = config
            self.file_config = False

        if "username" not in self.config:
            exit("[ERROR] Required configuration was not found: username")
        elif "password" not in self.config:
            exit("[ERROR] Required configuration was not found: password")
        elif "couchdb" not in self.config:
            exit("[ERROR] Required configuration was not found: couchdb")
        elif "author" not in self.config:
            exit("[ERROR] Required configuration was not found: author")
        elif "home_page_url" not in self.config:
            exit("[ERROR] Required configuration was not found: home_page_url")
        elif "feed_base_url" not in self.config:
            exit("[ERROR] Required configuration was not found: feed_base_url")

        else:
            self.api = feed_api.Api(
                self.config["couchdb"],
                self.config["username"],
                self.config["password"],
                self.config["author"],
                self.config["home_page_url"],
                self.config["feed_base_url"],
                ignore_ssl_errors=self.config["ignore_ssl_errors"]
                if "ignore_ssl_errors" in self.config
                else None,
                debug=self.config["debug"] if "debug" in self.config else False,
            )

    def load_config(self):
        with open(os.path.expanduser(CONFIG_FILE)) as json_file:
            self.config = json.load(json_file)

    def save_config(self):
        if self.file_config:
            with open(os.path.expanduser(CONFIG_FILE), "w") as outfile:
                json.dump(self.config, outfile)

    def new_channel(self):
        # First set the program as the active one
        
        channel = self.get_channel()        
        title = None
        description = None
        if self.arguments["-t"]:
            title = self.arguments["-t"]
        if self.arguments["-d"]:
            description = self.arguments["-t"]

        self.api.create_new_channel(
            channel, title=title, description=description
        )     
        self.use_channel(channel)   

    def use_channel(self, channel=None):
        if channel:
            self.config["channel"] = channel
        else:
            channel = self.arguments["<channel>"]
            self.config["channel"] = channel
        print(self.config["channel"])

    def get_channel(self):
        if "-c" in self.arguments and self.arguments["-c"]:
            return self.arguments["-c"]
        elif "channel" in self.config:
            return self.config["channel"]
        else:
            raise Exception("You need to select a channel to execute this action.")

    def add_url(self, url):
        channel_id = self.get_channel()
        include_full_content = False
        if "-f" in self.arguments and self.arguments["-f"]:
            include_full_content = True
        doc = self.api.scrape_document(url, include_full_content=include_full_content)
        self.api.upsert_new_item(channel_id, doc)

    def run(self):
        import pprint

        pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.arguments)

        if not self.config:
            try:
                self.load_config()
            except Exception:
                print(
                    "[WARNING] Could not read config file - make sure it exists and is readable"
                )

        if self.arguments["get"]:
            channel = self.get_channel()
            print("Current Channel: {}".format(channel))

        if self.arguments["new"]:
            self.new_channel()

        if self.arguments["use"]:
            self.use_channel()

        if self.arguments["add"]:
            if self.arguments["<url>"]:
                url = self.arguments["<url>"]
                self.add_url(url)
            else:
                print("[Error] Give url")

        try:
            print("Saving config")
            self.save_config()
        except Exception:
            print(
                "[WARNING] Could not write to config file - make sure it exists and is writable"
            )


def main():
    try:
        arguments = docopt(__doc__, version=VERSION)
        result = ReadlistClient(arguments).run()
        if result:
            if type(result) is list:
                print("\n".join(result))
            else:
                print(result)
    except Exception as e:
        print("[ERROR] " + str(e))


if __name__ == "__main__":
    main()
