import os
import yaml

from configs import (
    META_KEY_MAPPING_FILE,
)


class MetaKeyMappings(object):
    mapping_dict = None
    mappping_file = None

    def __init__(self):
        self.mappping_file = META_KEY_MAPPING_FILE

        self.load_mapping()

    def load_mapping(self):
        assert self.mappping_file is not None

        if not os.path.exists(self.mappping_file):
            self.mapping_dict = {}
            return

        with open(self.mappping_file, 'r') as f:
            self.mapping_dict = yaml.safe_load(f)

    def get_mapping_count(self):
        if not self.mapping_dict:
            return 0

        return len(self.mapping_dict)

    def check_key_conflict(self, old_key, new_key):
        if new_key in self.mapping_dict:
            raise Exception('key mapping conflict: new_key(%s) already renamed' % new_key)

    def update_mapping(self, old_key, new_key, check_conflict=True):
        if check_conflict:
            self.check_key_conflict(old_key, new_key)

        self.mapping_dict[old_key] = new_key

    def save(self):
        dirnpath = os.path.dirname(self.mappping_file)
        if not os.path.exists(dirnpath):
            os.makedirs(dirnpath)

        with open(self.mappping_file, 'w') as fw:
            yaml.dump(self.mapping_dict, fw)
