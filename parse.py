from requests import Session
from bs4 import BeautifulSoup as bs
from tkinter.filedialog import askdirectory
from tkinter import Tk


class Parse:
    def __init__(self) -> None:
        self.session = Session()
        self.url = 'https://www.wallpaperflare.com'
        self.rest_path = 'search'
        self.prompt = 'pixel art'
        self.upload_path = '.'
        self.page = 1
    
    def get_upload_path(self):
        root = Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        direct = askdirectory()
        if not direct:
            print('Aborting...')
            return -1
        return direct

    def create_url(self, rest_path=None, **params):
        if rest_path == None:
            rest_path = self.rest_path
        result_url = ''.join([self.url, rest_path if rest_path[0] == '/' else '/' + rest_path, '?'])
        keys_array = []
        for key, value in params.items():
            keys_array.append(f'{key}={str(value).replace(" ", "+")}')
        result_url += '&'.join(keys_array)
        return result_url
    
    def explore_last_page(self):
        print(f'Exploring pages for the "{self.prompt}"...')
        minn = 1
        maxx = 100
        request = self.session.get(self.create_url(wallpaper=self.prompt))
        if len(request.history):
            print(f'0 results for prompt "{self.prompt}"')
            return -1
        while True:
            request = self.session.get(self.create_url(wallpaper=self.prompt, page=maxx))
            if request.status_code == 200:
                minn = maxx
                maxx += 100
            else:
                break
        while minn + 1 != maxx:
            current = round(minn + ((maxx - minn) / 2))
            request = self.session.get(self.create_url(wallpaper=self.prompt, page=current))
            if request.status_code == 200:
                minn = current
            elif request.status_code == 404:
                maxx = current
        return minn
    
    def configure(self):
        print('Input search prompt(example: pixel art): ', end='')
        last_page = -1
        while last_page == -1:
            self.prompt = input()
            if self.prompt == '':
                self.prompt = 'pixel art'
            last_page = self.explore_last_page()
            if last_page == -1:
                print('Try other prompts(example: pixel art): ', end='')
        print(f'Choose the page (1-{last_page}): ', end='')
        while True:
            page_str = input()
            if page_str == 'exit':
                return -1
            elif page_str.isdigit() and 1 <= int(page_str) <= last_page:
                break
            else:
                print(f'Input must be integer positive number >=1 and <={last_page}["exit" to abort]: ')
        self.page = int(page_str)
        while True:
            path = self.get_upload_path()
            if path == -1:
                print('Incorrect input, do you want to try again? [yes]: ', end='')
                if input() != 'yes':
                    return -1
            else:
                self.upload_path = path
                break
        return 0

    def get_pages_urls(self):
        request = self.session.get(self.create_url(self.rest_path, wallpaper=self.prompt, page=self.page))
        soup = bs(request.text, 'html.parser')
        load_urls = []
        tags = soup.find_all('a', itemprop='url')
        for tag in tags:
            load_urls.append(tag['href'] + '/download')
        return load_urls

    def upload_images(self):
        if self.configure() == -1:
            print('Aborting...')
            return -1
        count = 0
        print(f'Downloading into: {self.upload_path}')
        urls = self.get_pages_urls()
        for url in urls:
            soup = bs(self.session.get(url).text, 'html.parser')
            image_url = soup.find('img', itemprop='contentUrl')['src']
            image = self.session.get(image_url).content
            with open(f'{self.upload_path}/image_{count}.jpg', 'wb') as pict:
                pict.write(image)
            print(f'Image {count + 1}/{len(urls)} downloaded')
            count += 1
            
parser = Parse()
parser.upload_images()