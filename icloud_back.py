import os
import sys
import time
import keyring
from pyicloud import PyiCloudService
from pyicloud.exceptions import (
    PyiCloudAPIResponseException , PyiCloudServiceNotActivatedException,
    PyiCloudFailedLoginException, PyiCloud2SARequiredException,
    PyiCloudNoStoredPasswordAvailableException, PyiCloudNoDevicesException
)

class IcloudBack:
    def __init__(self):
        self.photo_path = os.environ.get('PHOTO_PATH')
        if not self.photo_path:
            self.photo_path = './photos'

        self.backup_fre_in_min = os.environ.get('BACKUP_FRE_IN_MIN')
        if not self.backup_fre_in_min:
            self.backup_fre_in_min = 6 * 60

        self.data_file_path = './.icloud_backup_data'

    def data_exis(self):
        if os.path.exists(self.data_file_path):
            return True
        else:
            return False
        return False

def log_in(accout=None, password=None):
    api = None
    try:
        print(f'Begin logging in to your account:{accout}')
        if (password != None): # 首次登录
            api = PyiCloudService(accout, password, china_mainland=True)
        else: # 拥有cookies,无密码登录
            api = PyiCloudService(accout, china_mainland=True)
    except PyiCloudAPIResponseException:
        print('Login error, please check your account and password!')
    except PyiCloudServiceNotActivatedException:
        print('PyiCloud Service Not Activated Exception!')
    except PyiCloudFailedLoginException:
        print('PyiCloud Failed Login Exception!')
    except PyiCloud2SARequiredException:
        print('PyiCloud 2SA Required Exception!')
    except PyiCloudNoStoredPasswordAvailableException:
        print('PyiCloud No Stored Password Available Exception!')
    except PyiCloudNoDevicesException:
        print('PyiCloud No Devices Exception!')
    except:
        print('Unknown error!!')
        sys.exc_info()
    if api == None:
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

def download_photos(api : PyiCloudService, icloud_back:IcloudBack):
    photo_albums_keys = api.photos.albums.keys()
    for albums_dir in photo_albums_keys:
        album_path = os.path.join(icloud_back.photo_path, albums_dir)
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

def help_info():
    print('\nPlease initialize your account for the first login:')
    print("Enter: python icloud_back.py init")
    print("Then input your accout and password\n")

def first_log(args, icloud_back, debug_mode):
    if (debug_mode): # 调试模式, 直接给账户密码
        if len(args) >= 3:
            print(f'Account:{args[1]} Password:{args[2]}')
            username = args[1]
            password = args[2]
    else: # 正常模式,用户输入账户密码
        print("Please input your accout:")
        username = input()
        print("Please input your password:")
        password = input()
    api = log_in(username, password)
    with open(icloud_back.data_file_path, 'w') as f: # 将用户名记录到文件
        f.write(username)
    del api
    keyring.set_password("icloud", username, password)

    if not os.path.exists(icloud_back.data_file_path):
        help_info()
        exit(0)

def main():
    icloud_back = IcloudBack()
    debug_mode = 0 # 调试模式, 直接给账户密码
    if len(sys.argv) > 1: # 检查是否给了参数
        first_log(sys.argv, icloud_back, debug_mode) # 首次登录
    if not icloud_back.data_exis():
        help_info()
        exit(1)

    while True:
        with open(icloud_back.data_file_path, 'r') as f:
            username = f.read().strip()
            retrieved_password = keyring.get_password("icloud", username)
            api = log_in(username, retrieved_password)
            print(f'log suceess!')
        if api:
            print(f'start back-up photos...')
            download_photos(api, icloud_back)
            del api
            print(f'sync over, after {icloud_back.backup_fre_in_min} mins will sync again...')
            time.sleep(icloud_back.backup_fre_in_min*60)
        else:
            print('error, please init again, will exit...')
            exit(-1)

main()