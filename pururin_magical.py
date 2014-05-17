#!python/bin/python3
import click
import requests
import html5lib
import os
import os.path as osp
from slugify import slugify_filename
from mimetypes import guess_extension
from time import sleep as _sleep

headers = {
    'Host': 'pururin.com',
    'Referer': 'http://pururin.com/',
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:30.0) '
                   'Gecko/20100101 Firefox/30.0'),
}

ns = {
    'ns': 'http://www.w3.org/1999/xhtml',
}

x_name = '//ns:h1[@class="otitle"]/text()'
x_thumbs = ('//ns:a[starts-with(., "View all") and '
            'contains(., "thumbnails")]/@href')
x_pages = '//ns:ul[@class="thumblist"]/ns:li/ns:a/@href'
x_image = '//ns:a[@class="image-next"]/ns:img/@src'

path = osp.expanduser('~/Pururin')


def get_more(doc, sel):
    res = doc.xpath(sel, namespaces=ns)
    assert res
    return res


def get_one(doc, sel):
    res = get_more(doc, sel)[0]
    assert res
    return res


def rel_url(url):
    return 'http://pururin.com%s' % url


def page_fsname(fsname, i, ext):
    return '%s__%03d%s' % (fsname, i + 1, ext)


def has_page(fsname, i):
    for ext in ('.jpeg', '.png'):
        page_path = osp.join(path, fsname, page_fsname(fsname, i, ext))
        if osp.isfile(page_path):
            return page_path
    return False


@click.command()
@click.option('--sleep', default=1, help=('Delay requests for a given '
                                          'number of seconds.'))
@click.argument('url')
def cli(sleep, url):
    robot = requests.Session()
    click.echo('loading %s' % url)
    res = robot.get(url, headers=headers)
    assert res.status_code == 200

    html = html5lib.parse(res.text, treebuilder='lxml')
    name = get_one(html, x_name)
    click.echo('name: %s' % name)

    fsname = slugify_filename(name)
    save_path = osp.join(path, fsname)
    click.echo('save to: %s' % save_path)
    os.makedirs(save_path, exist_ok=True)

    thumbs_url = rel_url(get_one(html, x_thumbs))
    click.echo('pause')
    _sleep(sleep)

    click.echo('loading %s' % thumbs_url)
    headers['Referer'] = url
    res = robot.get(thumbs_url, headers=headers)
    assert res.status_code == 200

    html = html5lib.parse(res.text, treebuilder='lxml')
    pages = list(map(rel_url, get_more(html, x_pages)))
    assert pages
    click.echo('pages: %d' % len(pages))

    headers['Referer'] = thumbs_url
    for i, p in enumerate(pages):
        page_path = has_page(fsname, i)
        if page_path:
            click.echo('has page: %s' % page_path)
            continue

        click.echo('pause')
        _sleep(sleep)

        click.echo('loading %s' % p)
        res = robot.get(p, headers=headers)
        assert res.status_code == 200

        html = html5lib.parse(res.text, treebuilder='lxml')
        image_url = rel_url(get_one(html, x_image))
        click.echo('image: %s' % image_url)

        headers['Referer'] = p
        res = robot.get(image_url, headers=headers)
        assert res.status_code == 200
        assert int(res.headers['content-length']) == len(res.content)

        ext = guess_extension(res.headers['content-type'])
        if ext in ('.jpg', '.jpe'):
            ext = '.jpeg'
        image_path = osp.join(save_path, page_fsname(fsname, i, ext))
        click.echo('save to: %s' % image_path)
        with open(image_path, 'wb') as image:
            image.write(res.content)


    # from IPython import embed
    # embed()

if __name__ == '__main__':
    cli()
