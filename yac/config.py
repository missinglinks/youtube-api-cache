import yaml

def load_config(config_filepath):
    config = yaml.load(open(config_filepath))
    return config