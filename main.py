import requests
import hashlib
import os

with open('VKtoken.txt', 'r') as file_object:
    vktoken = file_object.read().strip()

with open('Yatoken.txt', 'r') as file_object:
    yatoken = file_object.read().strip()

with open('ok_token.txt', 'r') as file_object:
    oktoken = file_object.read().strip()

with open('ok_ssk.txt', 'r') as file_object:
    session_secret_key = file_object.read().strip()

with open('ok_app.txt', 'r') as file_object:
    ok_app_key = file_object.read().strip()


PHOTO_LIST = []


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_photos(self, user_id=None):

        downloading_list = []

        if user_id is None:
            user_id = self.owner_id
        photos_url = self.url + 'photos.get'
        offset = 0
        photos_param = {
            'owner_id': user_id,
            'album_id': 'profile',
            'offset': 0,
            'count': 2,
            'extended': 1
        }
        res = requests.get(photos_url, params={**self.params, **photos_param})
        res = res.json()
        count = res['response']['count']

        while offset <= count:
            photos_param = {
                'owner_id': user_id,
                'album_id': 'profile',
                'offset': offset,
                'count': 2,
                'extended': 1
            }
            res = requests.get(photos_url, params={**self.params, **photos_param})
            res = res.json()
            data = res['response']['items']
            for photo in data:
                file_name = str(photo['likes']['count']) + '.jpg'
                if file_name in PHOTO_LIST:
                    file_name = str(photo['likes']['count']) + '_' + str(photo['date']) + '.jpg'
                file_url = photo['sizes'][-1]['url']
                download_link = requests.get(file_url)
                PHOTO_LIST.append(file_name)
                downloading_list.append(file_name)

                with open(file_name, 'wb') as file:
                    file.write(download_link.content)
                print(f'{file_name} downloading complete.')
            print(f'Downloading complete. {len(downloading_list)} photos have been downloaded.')
            downloading_list.clear()
            offset = offset + photos_param['count']


class OkUser:
    url = 'https://api.ok.ru/fb.do'

    def __init__(self, token, session_key, app_key):
        self.token = token
        self.session_secret_key = session_key
        self.app_key = app_key
        self.base_params = {
            'application_key': self.app_key,
            'format': 'json',
            'method': 'users.getCurrentUser'
        }

        params_list = []

        for k, v in self.base_params.items():
            params_list.append(k + '=' + v)
        sig = (''.join(params_list) + session_secret_key)
        sig = str.encode(sig, encoding='utf-8')
        sig = hashlib.md5(sig).hexdigest()

        self.user_id_params = {
            'application_key': self.app_key,
            'format': 'json',
            'method': 'users.getCurrentUser',
            'sig': sig,
            'access_token': self.token
        }
        self.owner_id = requests.get(self.url, self.user_id_params).json()['uid']
        params_list.clear()

    def get_person_photo(self, user_id=None):

        if user_id is None:
            user_id = self.owner_id

        downloading_list = []

        base_params = {
            'application_key': self.app_key,
            'count': str(5),
            'detectTotalCount': 'True',
            'fid': user_id,
            'format': 'json',
            'method': 'photos.getPhotos'
        }

        params_list = []

        for k, v in base_params.items():
            params_list.append(k + '=' + v)
        sig = (''.join(params_list) + session_secret_key)
        sig = str.encode(sig, encoding='utf-8')
        sig = hashlib.md5(sig).hexdigest()

        album_params = {
            'application_key': self.app_key,
            'count': str(5),
            'detectTotalCount': 'True',
            'fid': user_id,
            'format': 'json',
            'method': 'photos.getPhotos',
            'sig': sig,
            'access_token': self.token
        }
        req = requests.get(self.url, album_params)
        req = req.json()
        count = req['totalCount']
        anchor = req['anchor']
        photos = req['photos']
        has_more = req['hasMore']

        for photo in photos:
            file_name = str(photo['mark_count']) + '.jpg'
            if file_name in PHOTO_LIST:
                file_name = str(photo['mark_count']) + '_' + str(photo['id']) + '.jpg'
            file_url = photo['pic640x480']
            download_link = requests.get(file_url)
            PHOTO_LIST.append(file_name)
            downloading_list.append(file_name)

            with open(file_name, 'wb') as file:
                file.write(download_link.content)
            print(f'{file_name} downloading complete.')

        offset = int(album_params['count'])

        while offset <= count:
            if has_more is True:

                params_list_anchor = []

                new_base_params = {
                    'anchor': anchor,
                    'application_key': self.app_key,
                    'count': str(5),
                    'detectTotalCount': 'True',
                    'direction': 'FORWARD',
                    'fid': user_id,
                    'format': 'json',
                    'method': 'photos.getPhotos'
                }

                for k, v in new_base_params.items():
                    params_list_anchor.append(k + '=' + v)

                sig = (''.join(params_list_anchor) + session_secret_key)
                sig = str.encode(sig, encoding='utf-8')
                sig = hashlib.md5(sig).hexdigest()
                params_list_anchor.clear()

                new_album_params = {
                    'anchor': anchor,
                    'application_key': self.app_key,
                    'count': str(5),
                    'detectTotalCount': 'True',
                    'direction': 'FORWARD',
                    'fid': user_id,
                    'format': 'json',
                    'method': 'photos.getPhotos',
                    'sig': sig,
                    'access_token': self.token
                }

                req = requests.get(self.url, new_album_params)
                req = req.json()

                photos = req['photos']

                for photo in photos:
                    file_name = str(photo['mark_count']) + '.jpg'
                    if file_name in PHOTO_LIST:
                        file_name = str(photo['mark_count']) + '_' + str(photo['id']) + '.jpg'
                    file_url = photo['pic640x480']
                    download_link = requests.get(file_url)
                    PHOTO_LIST.append(file_name)
                    downloading_list.append(file_name)

                    with open(file_name, 'wb') as file:
                        file.write(download_link.content)
                    print(f'{file_name} downloading complete.')

            anchor = req['anchor']
            has_more = req['hasMore']
            offset = offset + int(album_params['count'])
        print(f'Downloading complete. {len(downloading_list)} photos have been downloaded.')
        downloading_list.clear()


class YAUPLOADER:
    def __init__(self, token: str):
        self.token = token

    def upload(self):
        user_input = input('Введите команду:\n'
                           'current - для загрузки фотографий в корень Yandex Диск\n'
                           'new_folder - для загрузки фотографий в новую папку\n')
        if user_input == 'current':
            for photo in PHOTO_LIST:
                respon = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                      params={'path': photo, 'overwrite': 'true'},
                                      headers={"Authorization": f"OAuth {self.token}"})
                answer = respon.json()
                upload_link = answer['href']

                with open(photo, 'rb') as upload_photos:
                    requests.put(upload_link, files={'file': upload_photos})
                    print(f'{photo} uploading complete')
            print(f'uploading your profile photos from social network has been completed')


def selecting_folder():
    user_input = input('Куда сохранить фотографии:\n'
                       'folder - для просмотра выбранного пути\n'
                       'change - для смены пути (введите абсолютный путь)\n')
    if user_input == 'folder':
        print(f'Путь для скачивания фотографий:\n{os.getcwd()}')
        user_input = input('Введите:\nсonfirm - для подтверждения пути\nback - для возврата в предыдущие меню\n')
        if user_input == 'confirm':
            return f'фотографии будут сохранены в\n{os.getcwd()}'
        elif user_input == 'back':
            return selecting_folder()
    elif user_input == 'change':
        user_input = input('Введите путь куда вы желаете сохранить фотографии:\n')
        os.chdir(user_input)
        print(f'фотографии будут сохранены в {os.getcwd()}')
        user_input = input('Введите:\nсonfirm - для подтверждения пути\nback - для возврата в предыдущие меню\n')
        if user_input == 'confirm':
            return f'фотографии будут сохранены в\n{os.getcwd()}'
        elif user_input == 'back':
            return selecting_folder()


def main():
    while True:
        vkuser = VkUser(vktoken, '5.126')
        okuser = OkUser(oktoken, session_secret_key, ok_app_key)
        yan = YAUPLOADER(yatoken)
        user_input = input('Введите команду:\n'
                           'VK - для скачивания фотографий профиля с вКонтактке\n'
                           'OK - для скачивания фотографий профиля с Одноклассники\n'
                           'photos - для просмотра списка скаченных фото\n'
                           'exit - для выхода\n')
        if user_input == 'VK':
            print(selecting_folder())
            user_input = input('Введите id или username профиля, фотографии кторого вы хотите скачать:\n')
            vkuser.get_photos(user_input)
            user_input = input('Введите:\n'
                               'backup - для загрузки фоторграфий на Яндекс Диск\n'
                               'back - для возврата в предыдущие меню\n')
            if user_input == 'backup':
                yan.upload()
            elif user_input == 'back':
                main()
                break
        if user_input == 'OK':
            print(selecting_folder())
            user_input = input('Введите id или username профиля, фотографии кторого вы хотите скачать:\n')
            okuser.get_person_photo(user_input)
            user_input = input('Введите:\n'
                               'backup - для загрузки фоторграфий на Яндекс Диск\n'
                               'back - для возврата в предыдущие меню\n')
            if user_input == 'backup':
                yan.upload()
            elif user_input == 'back':
                main()
                break
        elif user_input == 'photos':
            print(PHOTO_LIST)
        elif user_input == 'exit':
            break


print(main())
