import requests
from django.conf import settings


def get_labels(item_list, lang):
    labels = {}
    item_ids = [item.wikidata_item for item in item_list if item.wikidata_item]

    for i in range(0, len(item_ids), 50):
        labels.update(fetch_labels(item_ids[i:i + 50], lang))

    return labels


def fetch_labels(item_ids, lang):
    params = {
        'action': 'wbgetentities',
        'ids': '|'.join(item_ids),
        'props': 'labels',
        'languages': lang,
        'format': 'json'
    }

    try:
        response = requests.get(settings.WIKIDATA_URL + '/w/api.php', params=params)
        data = response.json()
    except Exception:
        return {}

    if data['success'] != 1:
        return {}

    return {id: data['entities'][id]['labels'][lang]['value']
            for id in data['entities']}
