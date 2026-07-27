import yaml
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)
def get_categories():
    cfg = load_yaml('config/categories.yaml')
    return cfg['schedule'], cfg['tickers']