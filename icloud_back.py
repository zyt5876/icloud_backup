import os
import sys
import time
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException

class user_setting:
    def __init__(self):
        self.photo_path = os.environ.get('PHOTO_PATH')
        if not self.photo_path:
            self.photo_path = './photos'

        self.backup_fre_in_min = os.environ.get('BACKUP_FRE_IN_MIN')
        if not self.backup_fre_in_min:
            self.backup_fre_in_min = 6 * 60

        self.data_file_path = './.icloud_backup_data'

def log_in(accout, password='null'):
    try:
        api = PyiCloudService(accout, password)
    except PyiCloudAPIResponseException:
        print('Login error, please check your account and password!')
        exit(-1)
    except PyiCloudAPIResponseException:
        print('Login error, please check your account and password!')
    except:
        print('Unknown error!!')
        sys.exc_info()
        exit(-1)

    cookies = api.session.cookies
    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif api.requires_2sa:
        import click
        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s" % (i, device.get('deviceName',
                                            "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)
    return api

def download_photos(api : PyiCloudService, para:user_setting):
    photo_albums_keys = api.photos.albums.keys()
    for albums_dir in photo_albums_keys:
        album_path = os.path.join(para.photo_path, albums_dir)
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        photos = iter(api.photos.albums[albums_dir])
        for photo in photos:
            local_photo_path = os.path.join(album_path, photo.filename)
            if not os.path.exists(local_photo_path): #判断是否已经下载过
                try:
                    print('start download:  ', photo.filename)
                    download = photo.download()
                    with open(os.path.join(album_path, photo.filename), 'wb') as opened_file:
                        opened_file.write(download.raw.read())
                except PyiCloudAPIResponseException:
                    print("iCloud response error!!! ", photo.filename)

def main():
    para = user_setting()
    args = sys.argv
    if len(args) >= 3:
        print(f'Account:{args[1]} Password:{args[2]}')
        api = log_in(args[1].strip(), args[2].strip())
        with open(para.data_file_path, 'w') as f:
            f.write(args[1])
        del api

    if not os.path.exists(para.data_file_path):
        print('\nPlease initialize your account for the first login:')
        print("python icloud_back.py init [user_name] [password]\n\n")
        exit(0)

    while True:
        with open(para.data_file_path, 'r') as f:
            accout = f.read().strip()
            print(f'Begin logging in to your account:{accout}')
            api = log_in(accout)
            print(f'log suceess!')

        if api:
            print(f'start back-up photos...')
            download_photos(api, para)
            del api
            print(f'sync over, after {para.backup_fre_in_min} mins will sync again...')
            time.sleep(para.backup_fre_in_min*60)
        else:
            print('error, please init again, will exit...')
            exit(-1)

main()
