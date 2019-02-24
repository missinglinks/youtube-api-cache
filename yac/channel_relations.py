"""
ChannelRelations class

Fetches related channels for a specific YouTube seed channels:

* related channels
  channels based on the YouTube 'related channels' algorithm
* featured channels
  channels set as featured by the seed channel holder
* subscribed channels
  channels the seed channels is subscribed to
"""

from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
import requests
import time

class ChannelRelations:
    
    YOUTUBE = "https://www.youtube.com/channel/{id}"
    YOUTUBE_CHANNELS = "https://www.youtube.com/channel/{id}/channels"
    YOUTUBE_SUBSCRIPTIONS = "https://www.youtube.com/{slug}/channels?view=56&shelf_id=0"
    
    def __init__(self, channel_id, proxy=None):
        #self.yt = yt
        self.slug = "channel/{}".format(channel_id)
        self.channel_id = channel_id
        self.featured = True
        self.proxies = {}
        if proxy:
            self.proxies = {
                "https": proxy
            }

    def _is_channel_available(self, soup):
        alerts = soup.find_all("div", {"class": "yt-alert-content"})
        if len(alerts) == 2:
            return False
        return True          

    def _get_page(self, url, use_proxy=False):
        while True:
            try: 
                if use_proxy:
                    rsp = requests.get(url, proxies=self.proxies)
                else:
                    rsp = requests.get(url)
                return rsp
            except ProxyError:
                time.sleep(20)
                print("retry")
                continue
        
    def _extract_related_channels(self, soup):
        """
        Extracts and yield channel ids from related channels,
        skips popular channel list
        """
        popular_channels_header = [ "Beliebte Kanäle", "Popular channels" ]
        related_channels_header = [ "Ähnliche Kanäle", "Related channels" ]
        
        for related_channels_div in soup.find_all("div", {"class": "branded-page-related-channels"}):

            header = related_channels_div.find("h2").text.strip()
            #skip popular channel list
            if header in related_channels_header:
                for related_channel  in related_channels_div("li"):
                    channel_link = related_channel.find("a")
                    slug = channel_link["href"][1:]
                    name = related_channel.text.strip().split(" - ")[0]
                    #channel_id = normalize_slug(self.yt, slug)    
                    #print(name, slug)
                    yield name, slug           
        
    def _extract_featured_channels(self, soup):
        """
        Extracts and yield channel ids from related channels,
        skips popular channel list
        """
        popular_channels_header = [ "Beliebte Kanäle", "Popular channels" ]
        related_channels_header = [ "Ähnliche Kanäle", "Related channels" ]
        
        for related_channels_div in soup.find_all("div", {"class": "branded-page-related-channels"}):

            header = related_channels_div.find("h2").text.strip()
            #skip popular channel list
            if header not in related_channels_header and header not in popular_channels_header:
                #print(header)
                for related_channel  in related_channels_div("li"):
                    channel_link = related_channel.find("a")
                    slug = channel_link["href"][1:]
                    #channel_id = normalize_slug(self.yt, slug)     
                    name = related_channel.text.strip().split(" - ")[0]
                    yield name, slug
        
    def _extract_subscriptions(self, soup):
        for subscribed_channel in soup.find_all("h3", {"class": "yt-lockup-title" }):
            channel_link = subscribed_channel.find("a")
            slug = channel_link["href"][1:]
            self.subscribed_channels.add((channel_link.text.strip(), slug))
            #print(channel_name, slug)
            
    def _fetch_subscriptions(self, soup):
        
        self._extract_subscriptions(soup)

        load_more = soup.find("button", { "class": "load-more-button"} )
        while load_more:           
            load_more_url = load_more["data-uix-load-more-href"]
            rsp = self._get_page("https://youtube.com"+load_more_url, self.use_proxy)
            
            lm_soup = BeautifulSoup(rsp.json()["content_html"], "html.parser")
            self._extract_subscriptions(lm_soup)     
            
            #get load more button, if available
            lm_widget = BeautifulSoup(rsp.json()["load_more_widget_html"], "html.parser")
            load_more = lm_widget.find("button", { "class": "load-more-button"} )
        


    def fetch_channel_relations(self):
        self.use_proxy = False
        print("\tfetching related and featured channels")

        res = self._get_page(self.YOUTUBE.format(id=self.channel_id), self.use_proxy)
        soup = BeautifulSoup(res.text, "html.parser")

        if not self._is_channel_available(soup):
            print("using proxy")
            self.use_proxy = True
            res = self._get_page(self.YOUTUBE.format(id=self.channel_id), self.use_proxy)
            soup = BeautifulSoup(res.text, "html.parser")


        self.related_channels = set()

        if self._is_channel_available(soup):
            for channel_id in self._extract_related_channels(soup):
                self.related_channels.add(channel_id)

        self.featured_channels = set()
        if self._is_channel_available(soup):
            for channel_id in self._extract_featured_channels(soup):
                self.featured_channels.add(channel_id)

        print("\tfetching subscribed channels")        
        
        self.subscribed_channels = set()
        
        res = self._get_page(self.YOUTUBE_SUBSCRIPTIONS.format(slug=self.slug), self.use_proxy)
        soup = BeautifulSoup(res.text, "html.parser")     
        #if "This channel doesn't feature any other channels." not in soup.text and "Subscriptions" in soup.text:
        self._fetch_subscriptions(soup)

        return
        
    def to_json(self):
        return {
            "channel_id": self.channel_id,
            "slug": self.slug,
            "related_channels": list(self.related_channels),
            "featured_channels": list(self.featured_channels),
            "subscribed_channels": list(self.subscribed_channels)
        }

    def all_related_Channels(self):
        return list(self.related_channels.union(self.featured_channels, self.subscribed_channels))