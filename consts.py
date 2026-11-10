import os
import string

# Crawler
dread_link = "http://g66ol3eb5ujdckzqqfmjsbpdjufmjd5nsgdipvxmsh7rckzlhywlzlqd.onion"
tor_path = '/home/mazen/tor-browser/Browser'
tor_default_settings_path = f'{tor_path}/TorBrowser/Data/Browser/profile.default'
tor_binary_path = f"{tor_path}/firefox"
allow_duplicates = False
nr_login_repetition = 7
nr_loops_4_crawler = 50
browser_timeout = 100

# Data processing
perfect_size = 122
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = f"{ROOT_DIR}/data"
crawled_data_path = f"{ROOT_DIR}/crawled_data"
crawled_data_sub_dirs = os.listdir(crawled_data_path)
allowed_chars = string.digits + string.ascii_uppercase
encoded_chars = {char: allowed_chars.index(char) for char in allowed_chars}

# Model
image_width = 32
image_height = 32
image_depth = 3
epochs = 90
batch_size = 32
learning_rate = 1e-3
test_size = 0.1
random_state = 42
models_path = f"{ROOT_DIR}/models"
