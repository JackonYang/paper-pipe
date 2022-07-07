import hashlib
import os


def get_file_list(path, ext):
    if not os.path.exists(path):
        raise ValueError('dir not exists. path: %s' % path)

    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                file_list.append(os.path.join(root, file))
    return file_list


def get_filename_list(path, ext):
    if not os.path.exists(path):
        raise ValueError('dir not exists. path: %s' % path)

    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                file_list.append(file[:-len(ext)])
    return file_list


def md5_for_file(filename, block_size=256*128, hr=True):
    """calculate md5 of a file
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    if hr:
        return md5.hexdigest()
    return md5.digest()


def getSizeInNiceString(sizeInBytes):
    """ Convert the given byteCount into a string like: 9.9bytes/KB/MB/GB

    """
    for (cutoff, label) in [(1024*1024*1024, "GB"),
                            (1024*1024, "MB"),
                            (1024, "KB"),
                            ]:
        if sizeInBytes >= cutoff:
            return "%.1f %s" % (sizeInBytes * 1.0 / cutoff, label)

    if sizeInBytes == 1:
        return "1 byte"
    else:
        bytes = "%.1f" % (sizeInBytes or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'
