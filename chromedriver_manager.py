"""
@description: 用于自动下载chromedriver，
"""
import os
import re
import shutil
import zipfile
import requests
import platform


class ChromeDriverManager:
    def __init__(self, output_dir=None):
        """
        :param output_dir: driver下载目录文件夹
        """
        self.__BASIC_DIR = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.__BASIC_DIR, 'chromedriver') if not output_dir else output_dir

    def __get_vail_driver_path(self, webdriver_version: str):
        """
        根据给定的webdriver版本，获取有效的chromedriver路径
        """
        data = self.__get_download_need_info(webdriver_version)
        root_path = self.output_dir
        v_root_name = data['driver_root']
        v_file_name = data['driver_name']

        system = platform.system()
        v_root_list = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
        if system == 'Windows':
            own_ver = re.search(r'^[^.]*\.[^.]*\.', v_root_name).group(0)[:-1]
            for folder in v_root_list:
                match = re.search(r'^[^.]*\.[^.]*\.', folder).group(0)[:-1]
                if match == own_ver:
                    return os.path.join(root_path, v_root_name, v_file_name)
        if system == "Linux":
            own_ver = re.search(r'^linux[^.]*\.[^.]*\.', v_root_name).group(0)[:-1]
            for folder in v_root_list:
                print(folder)
                try:
                    match = re.search(r'^linux[^.]*\.[^.]*\.', folder).group(0)[:-1]
                    if match == own_ver:
                        return os.path.join(root_path, v_root_name, v_file_name)
                except:
                    pass
        return None

    def match_driver(self, webdriver_version):
        """
        匹配并返回有效的chromedriver路径，如果不存在则下载
        """
        if not self.__get_vail_driver_path(webdriver_version):
            self.download_chromedriver(webdriver_version)
        return self.__get_vail_driver_path(webdriver_version)

    @staticmethod
    def __request_to_download_zip_file_and_show_progress(zip_file_path, response):
        """
        下载zip文件并显示下载进度
        """
        with open(zip_file_path, 'wb') as zip_file:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0

            for data in response.iter_content(block_size):
                if data:
                    zip_file.write(data)
                    downloaded += len(data)
                    progress = (downloaded / total_size) * 100
                    filled_length = int(round(progress / 2))
                    progress_bar = "[" + "#" * filled_length + " " * (50 - filled_length) + "]"
                    percent = "{0:.2f}%".format(progress)
                    print(f"\r下载进度：{progress_bar} {percent}", end="")
                    if progress >= 100:
                        print()
                    else:
                        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def __move_driver_file_to_root_folder(folder_name: str, driver_name: str):
        """
        将下载的chromedriver文件移动到根文件夹
        """
        chromedriver_path = None
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                if file == driver_name:
                    chromedriver_path = os.path.join(root, file)
                    break
        if chromedriver_path:
            shutil.move(chromedriver_path, os.path.join(folder_name, driver_name))
            for root, dirs, files in os.walk(folder_name):
                for file in files:
                    if file != driver_name:
                        os.remove(os.path.join(root, file))
                for dir in dirs:
                    if os.path.join(root, dir) != folder_name:
                        shutil.rmtree(os.path.join(root, dir))

    def download_chromedriver(self, webdriver_version: str):
        """
        下载指定版本的chromedriver
        """
        data = self.__get_download_need_info(webdriver_version)
        root_path = self.output_dir
        v_root_name = data['driver_root']
        v_file_name = data['driver_name']
        download_filename = data['driver_download_zipfile_name']

        print(f"开始下载 ChromeDriver {webdriver_version}")
        d_url = self.__get_download_link(webdriver_version, download_filename)
        print(d_url)

        response = requests.get(d_url, stream=True)
        response.raise_for_status()

        v_root_path = os.path.join(root_path, v_root_name)
        os.makedirs(v_root_path, exist_ok=True)
        zip_file_path = os.path.join(v_root_path, download_filename)

        self.__request_to_download_zip_file_and_show_progress(zip_file_path=zip_file_path, response=response)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(v_root_path)

        self.__move_driver_file_to_root_folder(folder_name=v_root_path, driver_name=v_file_name)

        print(f"ChromeDriver {webdriver_version} 下载完成，路径：{v_root_path}")

    def __get_download_need_info(self, version):
        """
        获取下载chromedriver所需的版本信息
        """
        system = platform.system()
        if self.__is_lower_then_144(self.__convert_front_version(version)):
            return {
                'driver_root': f'linux{version}' if system == "Linux" else version if system == 'Windows' else version,
                'driver_download_zipfile_name': "chromedriver_linux64.zip" if system == 'Linux' else "chromedriver_win32.zip" if system == 'Windows' else "chromedriver_mac64.zip",
                "driver_name": "chromedriver" if system == 'Linux' else "chromedriver.exe" if system == 'Windows' else "webdriver"
            }
        else:
            return {
                'driver_root': f'linux{version}' if system == "Linux" else version if system == 'Windows' else version,
                'driver_download_zipfile_name': "chromedriver-linux64.zip" if system == 'Linux' else "chromedriver-win32.zip" if system == 'Windows' else "chromedriver-mac64.zip",
                "driver_name": "chromedriver" if system == 'Linux' else "chromedriver.exe" if system == 'Windows' else "webdriver"
            }

    @staticmethod
    def __is_lower_then_144(short_version):
        """
        判断版本是否低于114
        """
        return int(short_version) < 114

    @staticmethod
    def __convert_front_version(long_version):
        """
        转换版本号为短版本号
        """
        return re.search(r'^[^.]*\.[^.]*\.', long_version).group(0)[:-3]

    def __get_download_link(self, long_version, zipfile_name):
        """
        获取chromedriver的下载链接
        """
        v = self.__convert_front_version(long_version)
        if self.__is_lower_then_144(v):
            r = requests.get('https://registry.npmmirror.com/-/binary/chromedriver/').json()
            for item in r:
                if v + "." in item['name'][:5]:
                    var = item['name'][:-1]
                    return f'https://cdn.npmmirror.com/binaries/chromedriver/{var}/{zipfile_name}'
        else:
            r = requests.get('https://registry.npmmirror.com/-/binary/chrome-for-testing/').json()
            for item in r:
                if v + "." in item['name'][:5]:
                    var = item['name'][:-1]
                    d_type = "linux64" if "linux" in zipfile_name else "win32" if 'win' in zipfile_name else "win32"
                    return f'https://cdn.npmmirror.com/binaries/chrome-for-testing/{var}/{d_type}/{zipfile_name}'


if __name__ == "__main__":
    manager = ChromeDriverManager(output_dir=r'C:\Users\mk12327\Desktop\test\asd')
    print(manager.match_driver('89.0.4389.23'))
