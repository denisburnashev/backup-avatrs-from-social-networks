import requests
import os
import json
from pprint import pprint


with open('VKtoken.txt', 'r') as file_object:
    vktoken = file_object.read().strip()

with open('Yatoken.txt', 'r') as file_object:
    yatoken = file_object.read().strip()

photo_list = []

class VK_user:
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
            'owner_id': user_id,
            'album_id': 'profile',
            'offset': 0,
            'count': 50,
            'extended': 1
        }
        res = requests.get(photos_url, params={**self.params, **photos_param})
        res = res.json()
        data = res['response']['items']
        user_input = input('Куда схоранить фотографии:\n'
                           'current - для скачивания фотографий в корень программы\n'
                           'new_folder - для создания новой папки в корне программы\n'
                           'change - для смены пути скачивания фотографий(введите абсолютный путь)\n')
        if user_input == 'current':
            os.chdir('C:\home work\VK backup photos')
        elif user_input == 'new_folder':
            user_input = input('Введите название новой папки:\n')
            os.mkdir(user_input)
            os.chdir('C:\home work\VK backup photos\\'+user_input)
        elif user_input == 'change':
            user_input = input('Введите название пути куда вы желаете сохранить фотографии:\n')
            os.chdir(user_input)
        for photo in data:
            file_name = str(photo['likes']['count'])+'.jpg'
            file_url = photo['sizes'][-1]['url']
            download_link = requests.get(file_url)
            photo_list.append(file_name)

            with open(file_name, 'wb') as file:
                file.write(download_link.content)
            print(f'{file_name} downloading complete.')
        print(f'Downloading complete. {len(photo_list)} have been downloaded.')


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload(self):
        print(os.getcwd())
        for photo in photo_list:
            respon = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                params={'path': photo, 'overwrite':'true'},
                                headers={"Authorization": f"OAuth {self.token}"})
            answer = respon.json()
            upload_link = answer['href']

            with open(photo, 'rb') as upload_photos:
                requests.put(upload_link, files={'file': upload_photos})
                print(f'{photo} uploading complete')
        print(f'uploading your profile photos from vk has been completed')


def main():
    while True:
        vkuser = VK_user(vktoken, '5.126')
        yan = YaUploader(yatoken)
        user_input = input('Введите команду:\n'
                           'VK - для скачивания с вКонтактке\n'
                           'OK - для скачивания с Одноклассники\n'
                           'photos - для просмотра скаченных фото\n'
                           'exit - для выхода\n')
        if user_input == 'VK':
            user_input = input('Введите id профиля, фотографии кторого вы хотите скачать:\n')
            vkuser.get_photos(user_input)
            user_input = input('Введите:\n'
                               'backup - для загрузки фоторграфий на Яндекс Диск\n'
                               'back для возврата в предыдущие меню\n')
            if user_input == 'backup':
                yan.upload()
            elif user_input == 'back':
                main()
                break
        elif user_input == 'photos':
            print(photo_list)
        elif user_input == 'exit':
            break

print(main())
