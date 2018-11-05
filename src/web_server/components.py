

def serialize_options(options: dict):
    """
    given a dict and return html options
    :param options: dict with {key1: {'label': 'Label', 'selected': False}}
    :return: html options
    """
    res = []
    for k, v in options.items():
        cur = '<option value="{value}" {selected}>{label}</option>'.format(
            value=str(k),
            selected='selected="selected"' if v.get('selected') else '',
            label=str(v.get('label') or k)
        )
        res.append(cur)
    return '\n'.join(res)
