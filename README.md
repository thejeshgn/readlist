# Readlist 
This is a CLI for creating and managing [Readlist](https://thejeshgn.com/tag/readlists/).

# Required
- CouchDB to store the data. So you will need CouchDB. You could also use any other service that provides a restful CRUD service to a NoSQL DB.
- Each readlist (channel) is a document in the DB. It can have zero or more feed Items.
- `feed_base_url` from where you will serve the JSONFeed. Usually, we attach `channel_id` to form the full URL. You can have a simple serverless function to read the document from CouchDB to serve it. Or you can make a CDN do it.
- pipx is what I use to install the command

# Install
- Clone this project
- `cd to readlist`
- `pipx install .`
- try `readlist -h`

# Setup a config file
```json
{
    "couchdb": "https://courchdb-url.com/readlists",
    "username": "couchdb_user",
    "password": "couchdb_password",
    "channel": "current_channel.json",
    "author":
    {
        "name": "Thejesh GN",
        "url": "https://thejeshgn.com"
    },
    "home_page_url": "https://thejeshgn.com",
    "feed_base_url": "https://example.cdn.com/readlists/{0}",
    "debug": true
}
```

## Details
- feed_base_url - is where your readers will access the feed
- Rest of the configuration items are self explanatory


# Use
```
Readlist Client

Usage:
  readlist get
  readlist use <channel>
  readlist new -c <channel> -t <title> -d <description>
  readlist [-c <channel>] [-f] add <url> 

Options:
  -h --help            Show this screen.
  -v --version         Version of this program
  -c <channel>         Select a channel to limit the command to. Not required when the command "use" has been run before.
```

# Credits, Inspirations and Thanks
- Influenced heavily by [BBRF client](https://github.com/honoki/bbrf-client) and have also used the same project structure, code structure etc. Uses the same MIT license.
- Dave Winer for building feeds and inspiring all of us


# License
MIT license