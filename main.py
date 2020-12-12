import requests
import os
import json
from pprint import pprint


with open('VKtoken.txt', 'r') as file_object:
    vktoken = file_object.read().strip()

with open('Yatoken.txt', 'r') as file_object:
    yatoken = file_object.read().strip()

photo_list = []
photo_url_list = []

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
        for photo in data:
            file_name = str(photo['likes']['count'])+'.jpg'
            file_url = photo['sizes'][-1]['url']
            download_link = requests.get(file_url)
            photo_list.append(file_name)
            photo_url_list.append(file_url)

            with open(file_name, 'wb') as file:
                os.chdir('C:\home work\VK backup photos\images')
                file.write(download_link.content)
            print(f'{file_name} загружено.')
        print(f'Downloading complete. {len(photo_list)} have been downloaded.')


# class YaUploader:
#     def __init__(self, token: str):
#         self.token = token
#
#     def upload(self):
#         file_path = input('Введите имя файла для загрузки: ')
#         respon = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
#                             params={'path': file_path, 'overwrite':'true'},
#                             headers=self.token)
#         respon.raise_for_status()
#         answer = respon.json()
#         pprint(answer)
#         upload_link = answer['href']





vkuser = VK_user(vktoken, '5.126')
print(vkuser.get_photos(14869974))
# yan = YaUploader({'toekn'})
# print(yan.upload())