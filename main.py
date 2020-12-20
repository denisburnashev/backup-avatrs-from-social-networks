import requests
import os

with open('VKtoken.txt', 'r') as file_object:
    vktoken = file_object.read().strip()

with open('Yatoken.txt', 'r') as file_object:
    yatoken = file_object.read().strip()

PHOTO_LIST = []


class VK_USER:
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
        if user_id is None:
            user_id = self.owner_id
        photos_url = self.url + 'photos.get'
        photos_param = {
            'owner_ids': user_id,
            'album_id': 'profile',
            'offset': 0,
            'count': 50,
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

            with open(file_name, 'wb') as file:
                file.write(download_link.content)
            print(f'{file_name} downloading complete.')
        print(f'Downloading complete. {len(PHOTO_LIST)}photos have been downloaded.')


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
        vkuser = VK_USER(vktoken, '5.126')
        yan = YAUPLOADER(yatoken)
        user_input = input('Введите команду:\n'
                           'VK - для скачивания фотографий профиля с вКонтактке\n'
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
        elif user_input == 'photos':
            print(PHOTO_LIST)
        elif user_input == 'exit':
            break


print(main())
