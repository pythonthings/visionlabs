import os
from requests import post, HTTPError, ConnectionError, TooManyRedirects, RequestException
from multiprocessing.pool import ThreadPool
import tqdm
import os
import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# ===
# logging!
__logfile = './upload.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# console
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# file
fl = logging.FileHandler(__logfile, encoding='utf-8')
fl.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fl.setFormatter(formatter)
logger.addHandler(fl)

# ===
# Configurable parameters
url = "https://example.com/images"
extensions = ['.jpg', '.jpeg', '.bmp', '.gif', '.tiff']

upload_processes = 10

def single_upload(file_name):
    base_filename = os.path.basename(file_name)
    logger.info(f"Start uploading {base_filename}...")

    try:
        files = {'file': (base_filename, open(file_name, 'rb'))}
    except FileNotFoundError:
        logger.warning(f"File not found - {file_name}. Maybe deleted before uploading?")
        return
    except PermissionError:
        logger.warning(f"No permission to file - {file_name}")
        return
    except IOError:
        logger.warning(f"I\\O error while reading file - {file_name}")
        return
    except OSError:
        logger.warning(f"General error while reading file - {file_name}")
        return

    try:
        post(url, files=files)
    except ConnectionError as e:
        # if network problem then further uploads have no sense
        logger.exception(
            f"No connection to server when tried to upload file \"{base_filename}\". Exiting...")
        os._exit(1)
    except {HTTPError, TooManyRedirects, RequestException} as e:
        logger.warning(
            f"Request closed for file \"{base_filename}\" with exception: \n"
            + str(e))
        return

    logger.info(f"File {file_name} completely uploaded.")


if __name__ == '__main__':
    # parse arguments
    parser = ArgumentParser(
        prog='starter', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--threads', type=int, default=upload_processes,
                        help='Number of uploading threads')
    parser.add_argument('--dir', type=str, required=True,
                        help='Directory to upload files from.')
    ns = parser.parse_args()

    upload_processes = ns.threads
    files_dir = ns.dir

    # search files in directory
    try:
        files = os.listdir(files_dir)
    except FileNotFoundError:
        logger.exception(f"No such directory - {files_dir}")
        os.exit(1)
    except PermissionError:
        logger.exception(f"No permission to directory - {files_dir}")
        os.exit(1)
    except OSError:
        logger.exception(f"General error listing directory - {files_dir}")
        os.exit(1)

    files = filter(lambda x: os.path.splitext(x)[1] in extensions, files)
    files = map(lambda x: os.path.join(files_dir, x) , files)
    files = list(files)

    # upload files
    mp_pool = ThreadPool(upload_processes)
    for v in tqdm.tqdm(mp_pool.imap(single_upload, files), total=len(files)):
        pass
    logger.info('FINISHED!')
