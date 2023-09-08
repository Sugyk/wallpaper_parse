import requests

from requests import Session
from bs4 import BeautifulSoup as bs

session = Session()

urls = []

request = session.get('https://www.wallpaperflare.com/search?wallpaper=pixel+art')

soup = bs(request.text, 'html.parser')

load_urls = []
tags = soup.find_all('a', itemprop='url')

for tag in tags:
    load_urls.append(tag['href'] + '/download')

url = load_urls[0]
count = 0
for url in load_urls:
    soup = bs(session.get(url).text, 'html.parser')
    image_url = soup.find('img', itemprop='contentUrl')['src']
    image = session.get(image_url).content
    with open(f'wallpapers/image_{count}.jpg', 'wb') as pict:
        pict.write(image)
    count += 1
    
