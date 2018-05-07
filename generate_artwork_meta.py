from utils import read_prefs_data
import urllib2
import json
import csv

PREF_CSV_PATH = './data/prefs2080423.csv'
ARTWORK_CSV_PATH = './data/artwork_data.csv'
BASE_ELASTIC_URL = 'https://search.artsmia.org/ids/'


def batch(iterable, n=1):
    current_batch = []
    for item in iterable:
        current_batch.append(item)
        if len(current_batch) == n:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch

def get_artwork_data_from_elastic_search(artwork_ids):
    # Batch into chunks of 20
    # return { artworks: json.hits.hits }; artwork._source.id

    collected_data = {}

    for ids in batch(artwork_ids, n=50):
        response = urllib2.urlopen(BASE_ELASTIC_URL + ','.join(ids))
        json_data = json.loads(response.read())
        results = json_data['hits']['hits']
        for r in results:
            id = r['_source']['id']
            title = r['_source']['title']
            artist = r['_source']['artist']
            room = r['_source']['room']
            collected_data[id] = {'id': id, 'title': title, 'artist': artist, 'room': room}  # [u'inscription', u'artist_suggest', u'classification', u'text', u'image', u'culture', u'public_access', u'related:exhibitions', u'id', u'style', u'title', u'restricted', u'image_width', u'continent', u'object_name', u'role', u'department', u'medium', u'description', u'creditline', u'life_date', u'markings', u'nationality', u'image_copyright', u'curator_approved', u'room', u'artist', u'country', u'rights', u'accession_number', u'signed', u'catalogue_raissonne', u'image_height', u'dated', u'dimension']
    return collected_data

def collect_item_ids(prefs_data):
    collected_ids = set()
    for pref_data in prefs_data:
        collected_ids.add(pref_data.get('item_id', None))

    return collected_ids

def generate_csv(data):
    with open(ARTWORK_CSV_PATH, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('id', 'title', 'artist', 'room'))
        for vals in data.values():
            writer.writerow((vals['id'], vals['title'].encode('utf-8'), vals['artist'].encode('utf-8'), vals['room']))


def main():
    print 'Starting Process to get Artwork CSV Data'
    pref_data = read_prefs_data(PREF_CSV_PATH, skip_admin_survey=False)
    collected_ids = collect_item_ids(pref_data)

    print 'Prefs data contains %s unique artworks' % len(collected_ids)
    print collected_ids
    print 'Retrieving artwork data from elastic search in batches'
    data = get_artwork_data_from_elastic_search(collected_ids)

    print 'Data Retrieved. Generating CSV'
    generate_csv(data)

    print 'CSV generated to %s ' % ARTWORK_CSV_PATH

if __name__ == "__main__":
    main()
