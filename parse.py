from requests import Session
from bs4 import BeautifulSoup as bs
from tkinter.filedialog import askdirectory
from tkinter import Tk
import threading


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

    def tread_get_urls(self, start, end):
        print(self, start, end)
        for tag in range(start, end):
            soup = bs(self.session.get(self.tags[tag]['href'] + '/download').text, 'html.parser')
            self.urls[tag] = soup.find('img', itemprop='contentUrl')['src']

    def get_pages_urls(self):
        request = self.session.get(self.create_url(self.rest_path, wallpaper=self.prompt, page=self.page))
        soup = bs(request.text, 'html.parser')
        self.tags = soup.find_all('a', itemprop='url')
        self.urls = [None] * len(self.tags)
        len_tags = len(self.tags)
        threads_number = 5
        ranges = [[i * len_tags // threads_number, (i + 1) * len_tags // threads_number] for i in range(threads_number)]
        ranges[-1][-1] += len_tags % threads_number
        threads = []
        for i in range(threads_number):
            threads.append(threading.Thread(target=self.tread_get_urls, args=(ranges[i])))
        for i in range(threads_number):
            threads[i].start()
        for i in range(threads_number):
            threads[i].join()



    def uploading(self, start, end):
        print(self, start, end)
        filename = '-'.join(self.prompt.split())
        for url_pos in range(start, end):
            image = self.session.get(self.urls[url_pos]).content
            with open(f'{self.upload_path}/{filename}_p{self.page}_{url_pos}.jpg', 'wb') as pict:
                pict.write(image)
            print(f'Image {self.download}/{len(self.urls)} downloaded')
            self.download += 1

    def upload_images(self):
        if self.configure() == -1:
            print('Aborting...')
            return -1
        print(f'Downloading into: {self.upload_path}')
        print('Getting urls...')
        self.get_pages_urls()
        page_length = len(self.urls)
        threads_number = 5
        ranges = [[i * page_length // threads_number, (i + 1) * page_length // threads_number] for i in range(threads_number)]
        ranges[-1][-1] += page_length % threads_number
        self.download = 1
        for i in range(threads_number):
            threading.Thread(group=None, target=self.uploading, args=(ranges[i])).start()
        threading.Thread(group=None, target=lambda: input, args=(), daemon=True).start()
        
if __name__ == '__main__':
    parser = Parse()
    parser.upload_images()