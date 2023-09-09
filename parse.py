from requests import Session
from bs4 import BeautifulSoup as bs
from tkinter.filedialog import askdirectory


class Parse:
    def __init__(self) -> None:
        self.session = Session()
        self.url = 'https://www.wallpaperflare.com'
    
    def get_upload_path(self):
        return askdirectory()

    def create_url(self, rest_path, **params):
        result_url = ''.join([self.url, rest_path if rest_path[0] == '/' else '/' + rest_path, '?'])
        keys_array = []
        for key, value in params.items():
            keys_array.append(f'{key}={value.replace(" ", "+")}')
        result_url += '&'.join(keys_array)
        print(result_url)
        return result_url

    def get_pages_urls(self):
        request = self.session.get(self.url + '/search?wallpaper=pixel+art')
        soup = bs(request.text, 'html.parser')
        load_urls = []
        tags = soup.find_all('a', itemprop='url')
        for tag in tags:
            load_urls.append(tag['href'] + '/download')
        return load_urls

    def upload_images(self):
        count = 0
        path = self.get_upload_path()
        print(f'Downloading into: {path}')
        urls = self.get_pages_urls()
        for url in urls:
            soup = bs(self.session.get(url).text, 'html.parser')
            image_url = soup.find('img', itemprop='contentUrl')['src']
            image = self.session.get(image_url).content
            with open(f'{path}/image_{count}.jpg', 'wb') as pict:
                pict.write(image)
            print(f'Image {count + 1}/{len(urls)} downloaded')
            count += 1
            
parser = Parse()
parser.upload_images()