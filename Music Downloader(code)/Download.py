import mutagen.id3
import urllib.request
import yandex_music.exceptions

import Default
import Search
import DataBase


def set_path(client, path=None):
    if path is None:
        path = client.download_path()
    return path


def set_image(track, path):
    image_file = urllib.request.urlopen(track['image_link']).read()
    audio = mutagen.id3.ID3()
    audio.save(path)
    audio = mutagen.id3.ID3(path)
    audio.add(mutagen.id3.APIC(3, 'image/png', 3, 'uCover', image_file))
    return audio


def download_track(client, track, path=None):  # track downloader
    path = set_path(client, path) / f"{track['title']}_{track['id']}.mp3"  # path to downloaded files
    track['track'].download(path)  # track download
    audio = set_image(track, path)  # add track image
    audio.add(mutagen.id3.TIT2(text=f"{track['title']}"))  # add track title
    audio.add(mutagen.id3.TALB(text=f"{', '.join(track['album'])}"))  # add track album
    audio.add(mutagen.id3.TCON(text=f"{', '.join(track['genre'])}"))  # add track genre
    audio.add(mutagen.id3.TPE1(text=f"{', '.join(track['author'])}"))  # add track artists
    audio.add(mutagen.id3.TYE(text=f"{', '.join(track['year'])}"))  # add track data
    audio.save(v2_version=3)
    add_attribute_in_db(track)


def download_cover(client, track, path=None, size='1000x1000'):  # cover downloader
    path = set_path(client, path) / f"{track['title']}_{track['id']}"
    track['track'].download_cover(f"{path}.png", size)
    add_attribute_in_db(track)


def download_lyric(client, track, path=None):  # lyric downloader
    path = set_path(client, path) / f"{track['title']}_{track['id']}.txt"
    try:
        with open(path, 'w', encoding='utf8') as lyric_file:
            lyric = '\n'.join([i[11::] for i in track['track'].get_lyrics('LRC').fetch_lyrics().split('\n')])
            print(lyric, file=lyric_file)
            add_attribute_in_db(track)
    except yandex_music.exceptions.NotFoundError:
        raise yandex_music.exceptions.NotFoundError('no text???')


def add_attribute_in_db(track):
    DataBase.update_db(track['author'], track['album'], track['image_link'], track['title'])


if __name__ == '__main__':
    cli = Default.Default()
    current_track = Search.search(cli, 'война ksb')[0]
    download_track(cli, current_track)
    download_cover(cli, current_track)
    download_lyric(cli, current_track)
