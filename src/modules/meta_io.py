import yaml

yaml_dump_kwargs = {
    'width': 9999,
    'default_flow_style': False,
    'allow_unicode': True,
}


def dump(data, fw=None):
    return yaml.dump(data, fw, **yaml_dump_kwargs)


def safe_load(str_data):
    return yaml.safe_load(str_data)
