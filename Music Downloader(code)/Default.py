import pathlib
import yandex_music

import yandex_music.exceptions


class Default:
    def __init__(self, path=pathlib.Path('.MScache')):
        self.config_name = 'config'
        self.default_path = pathlib.Path(path)

        self.user_token = None
        self.default_download_path = None
        self.client = None

    def init_config(self, token=None, download_directory=None, reset_config=False):
        if not self.config_enabled() or reset_config:
            try:
                self.set_config(token, download_directory)
            except yandex_music.exceptions.UnauthorizedError:
                raise yandex_music.exceptions.UnauthorizedError
        with open(self.config(), 'r') as config:
            config_information = config.readlines()
            self.user_token = config_information[0][:-1]
            self.default_download_path = config_information[1]
        try:
            self.client = yandex_music.Client(self.user_token).init()
        except yandex_music.exceptions.UnauthorizedError:
            print('Введен неверный токен')

    def config_enabled(self):
        try:
            pathlib.Path(self.default_path / self.config_name).read_text()
            return True
        except FileNotFoundError:
            return False

    def set_config(self, token, download_directory):
        try:
            yandex_music.Client(token).init()
            with open(self.config(), 'w') as config:
                print(token, file=config)
                if download_directory is None:
                    download_directory = self.set_default_download_path()
                print(download_directory, file=config)
        except yandex_music.exceptions.UnauthorizedError:
            raise yandex_music.exceptions.UnauthorizedError

    def set_default_download_path(self):
        return self.path() / 'download'

    def token(self):
        return self.user_token

    def path(self):
        return self.default_path

    def config(self):
        return pathlib.Path(self.default_path / self.config_name)

    def download_path(self):
        return pathlib.Path(self.default_download_path[:-1])

    def edit_download_path(self, new_path):
        with open(self.config(), 'w') as config:
            print(self.user_token, file=config)
            print(pathlib.Path(new_path), file=config)


if __name__ == '__main__':
    defu = Default()
    defu.init_config('fw')
    print(defu.token())
    print(defu.path())
    print(defu.config())
    print(defu.download_path())
