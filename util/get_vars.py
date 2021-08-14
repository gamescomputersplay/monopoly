# https://stackoverflow.com/a/28150307/10629176
def get_vars(module):
    return {key: value for key, value in module.__dict__.items() if not (key.startswith('__') or key.startswith('_'))}
