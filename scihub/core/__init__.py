import io
import os

from matplotlib import pylab

import click
import bs4
import requests
from PIL import Image

from webrequests import WebRequest as WR
from simple_loggers import SimpleLogger

from scihub.util.host import check_host


class SciHub(object):
    def __init__(self, url=None, timeout=10):
        self.timeout = timeout
        self.logger = SimpleLogger('SciHub')
        self.url = url or self.check_url(url)

    def check_url(self, url):
        def _check(url):
            self.logger.info(f'checking url: {url} ...')
            try:
                resp = requests.get(url, timeout=self.timeout)
                elapsed = resp.elapsed.total_seconds()

                soup = bs4.BeautifulSoup(resp.text, 'html.parser')

                form = soup.select_one('form[method="POST"]')
                if form:
                    self.logger.info(f'good url: {url} [{elapsed}s]')
                    return elapsed

            except Exception as e:
                self.logger.warning(e)

            self.logger.warning(f'bad url: {url}')
            return None

        self.logger.info('checking url automaticlly ...')
        hosts, update_time = check_host()
        self.logger.debug(f'update time: {update_time}')

        for host in hosts:
            elapsed = _check(host)
            if elapsed:
                url = host
                break

        if not url:
            self.logger.error('no available url, please use -c to check')
            exit(1)

        self.logger.info(f'use url: {url}')
        return url

    def search(self, term, max_try=3):
        """
            term: URL, PMID, DOI or search string

            return: the url of pdf
        """
        soup = WR.get_soup(self.url)
        form = soup.select_one('form[method="POST"]')
        post_url = self.url if form.attrs['action'] == '/' else form.attrs['action']

        payload = {
            'sci-hub-plugin-check': '', 
            'request': term
        }

        self.logger.debug(f'search pdf url for: {term}')

        while max_try:
            max_try -= 1

            soup = WR.get_soup(post_url, method='POST', data=payload, timeout=self.timeout)

            pdf = soup.select_one('#pdf')

            if 'article not found' in soup.text:
                self.logger.warning(f'article not found [{term}]')
                return
            elif not pdf:
                # print(soup.select('title'))
                continue

            pdf_url = pdf.attrs['src']

            if pdf_url.startswith('//'):
                pdf_url = post_url.split(':')[0] + f':{pdf_url}'
            
            self.logger.info(f'pdf url: {pdf_url}')
            return pdf_url

        self.logger.error(f'your searching has no result, please check! [{term}]')

    def download(self, url, outdir='.', filename=None, chunk_size=512, overwrite=None, show_progress=True):
        """download pdf from url
        """
        filename = filename or os.path.basename(url).split('#')[0]
        if outdir != '.' and not os.path.exists(outdir):
            os.makedirs(outdir)

        outfile = os.path.join(outdir, filename)
        if os.path.isfile(outfile) and os.stat(outfile).st_size > 0:
            if not isinstance(overwrite, bool):
                overwrite = click.confirm('The file already exists, do you want to overwrite it?')

            if overwrite:
                self.logger.debug(f'overwriting the file: {outfile}')
            else:
                self.logger.debug(f'skip downloading file: {outfile}')
                return True
    
        resp = WR.get_response(url, stream=True)

        if resp.headers['Content-Type'] != 'application/pdf':
            resp = self.deal_captcha(url, outdir, filename, chunk_size)

        length = int(resp.headers.get('Content-Length'))

        # if os.path.isfile(outfile) and os.stat(outfile).st_size == length:

        self.logger.info(f'downloading pdf: {outfile} [{length/1024/1024:.2f} M]')

        bar = click.progressbar(length=length, label='downloading', show_percent=True, show_pos=True, show_eta=True)
        with open(outfile, 'wb') as out, bar:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                out.write(chunk)
                if show_progress:
                    bar.update(chunk_size)

        self.logger.info(f'save file: {outfile}')
        return True

    def deal_captcha(self, url, outdir, filename, chunk_size):
        """deal with the captcha
        """
        soup = WR.get_soup(url)
        img = soup.select_one('#captcha').attrs['src']
        img_url = url.rsplit('/', 3)[0] + img
        # print(img_url)

        self.logger.warning(f'need to type in the captcha: {img_url}')
        if os.getenv('DISPLAY'):
            self.logger.info(f'failed to open the picture, you can open it in your browser: {img_url}')
        else:
            content = WR.get_response(img_url, max_try=1).content
            im = Image.open(io.BytesIO(content))

            # im.show()  # this will block the program
            im.save('tmp.png')

            # ****************************
            # ***** non-blocked mode *****
            # ****************************
            pylab.ion()
            img = pylab.imread('tmp.png')

            pylab.imshow(img)
            pylab.show()

        while True:
            answer = click.prompt('please input the captcha')

            if answer == 'new':
                return self.download(url, outdir=outdir, filename=filename, chunk_size=chunk_size)

            payload = {
                'id': img_url.split('/')[-1].split('.')[0],
                'answer': answer
            }

            # payload = {'id': '6058249282282', 'answer': 'manila'}
            self.logger.debug(payload)

            resp = WR.get_response(url, method='POST', stream=True, data=payload)

            if resp.headers['Content-Type'] == 'application/pdf':
                pylab.close()
                return resp

            self.logger.warning('bad captcha, try again!')


if __name__ == '__main__':
    # sh = SciHub(url='https://scihub.bad')
    # sh = SciHub()
    # sh = SciHub(url='https://sci-hub.ai')
    sh = SciHub(url='https://sci-hub.ee')

    for term in range(26566462, 26566482):
        pdf_url = sh.search(term)
        if pdf_url:
            sh.download(pdf_url)
