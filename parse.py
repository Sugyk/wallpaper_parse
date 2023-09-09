from requests import Session
from bs4 import BeautifulSoup as bs


class Parse:
    def __init__(self) -> None:
        self.session = Session()

    def get_pages_urls(self):
        request = self.session.get('https://www.wallpaperflare.com/search?wallpaper=pixel+art')
        soup = bs(request.text, 'html.parser')
        load_urls = []
        tags = soup.find_all('a', itemprop='url')
        for tag in tags:
            load_urls.append(tag['href'] + '/download')
        return load_urls

    def upload_images(self):
        count = 0
        for url in self.get_pages_urls():
            soup = bs(self.session.get(url).text, 'html.parser')
            image_url = soup.find('img', itemprop='contentUrl')['src']
            image = self.session.get(image_url).content
            with open(f'wallpapers/image_{count}.jpg', 'wb') as pict:
                pict.write(image)
            count += 1
            
parser = Parse()
parser.upload_images()