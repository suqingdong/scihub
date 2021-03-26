import os
import sys
import time
import random
from collections import defaultdict

import click
import colorama
from simple_loggers import SimpleLogger

from scihub import version_info
from scihub.core import SciHub
from scihub.util.host import check_host


colorama.init()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

prog = version_info['prog']
author = version_info['author']
author_email = version_info['author_email']

__epilog__ = click.style(f'''\
Examples:

\b
* check the available urls
{colorama.Fore.CYAN}  {prog} -c  {colorama.Fore.RESET}

\b
* search pmid(s)
{colorama.Fore.CYAN}  {prog} -s 1,2,3  {colorama.Fore.RESET}

\b
* search doi(s)
{colorama.Fore.CYAN}  {prog} -s 10.1038/s41524-017-0032-0  {colorama.Fore.RESET}

\b
* search with a specific url
{colorama.Fore.CYAN}  {prog} -s 1,2,3 -u https://sci-hub.ren  {colorama.Fore.RESET}

{colorama.Fore.YELLOW}
Contact: {author} <{author_email}>
{colorama.Fore.RESET}
''')

@click.command(no_args_is_help=True,
               context_settings=CONTEXT_SETTINGS,
               epilog=__epilog__,
               help=click.style(version_info['desc'], fg='green', bold=True))
@click.option('-s', '--search', help='the string or file to search')
@click.option('-O', '--outdir', help='the output directory', default='pdf', show_default=True)
@click.option('-u', '--url', help='the url of sci-hub, eg. https://sci-hub.ee, automaticlly default')
@click.option('-l', '--list', help='list only but not download the pdf', is_flag=True)
@click.option('-c', '--check', help='check available urls of scihub', is_flag=True)
@click.option('-ns', '--name-by-search', help='name by search string', is_flag=True)
@click.option('-ow', '--overwrite', help='overwrite or not when file exists', type=click.Choice('YN'))
@click.option('-t', '--timeout', help='the seconds of timeout for requesting', type=int, default=60, show_default=True)
@click.version_option(version=version_info['version'], prog_name=version_info['prog'])
def cli(**kwargs):
    start_time = time.time()
    logger = SimpleLogger('Main')

    # checking the available urls
    if kwargs['check']:
        urls, update_time = check_host()
        print(f'last check time: {update_time}')
        print('\n'.join(['\t'.join(item) for item in urls.items()]))
        exit(0)

    logger.info(f'input arguments: {kwargs}')

    # collecting the search list
    search = kwargs['search'] or click.prompt('input the search')
    if search == '-' and not sys.stdin.isatty():
        search_list_temp = [line.strip() for line in sys.stdin]
    elif os.path.isfile(search):
        search_list_temp = [line.strip() for line in open(search)]
    else:
        search_list_temp = search.strip().split(',')

    # remove duplicate
    search_list = []
    for each in search_list_temp:
        if each not in search_list:
            search_list.append(each)

    logger.info(f'{len(search_list)} to search: {search_list[:5]} ...')

    # checking overwrite or not
    overwrite = kwargs['overwrite']
    if overwrite == 'Y':
        overwrite = True
    elif overwrite == 'N':
        overwrite = False

    sh = SciHub(url=kwargs['url'], timeout=kwargs['timeout'])

    stat = defaultdict(list)
    for n, search in enumerate(search_list, 1):
        logger.debug(f'[{n}/{len(search_list)}] searching: {search}')
        url = sh.search(search)
        if url:
            if kwargs['list']:
                logger.info(f'{search}: {url}')
            else:
                filename = f'{search}.pdf' if kwargs['name_by_search'] else None
                sh.download(url, outdir=kwargs['outdir'], filename=filename, overwrite=overwrite)
            stat['success'].append(search)
        else:
            stat['failed'].append(search)
        
        if n < len(search_list):
            time.sleep(random.randint(3, 8))

    logger.info(f'success: {len(stat["success"])}, failed: {len(stat["failed"])}')
    if stat['failed']:
        logger.info('failed list: {", ".join(stat["failed"])}')

    elapsed = time.time() - start_time
    logger.info(f'time elapsed: {elapsed:.2f}s')


def main():
    cli()


if __name__ == "__main__":
    main()