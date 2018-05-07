from utils import read_prefs_data
import urllib2
import json
import csv
from utils import read_artwork_data
from utils import read_prefs_data
from math import sqrt

PREF_CSV_PATH = './data/prefs2080423.csv'
ARTWORK_CSV_PATH = './data/artwork_data.csv'
ARTWORK_GALLERY_LIKES_DISLIKES_CSV_PATH = './output/artwork_gallery_likes_dislikes.csv'

ARTWORK_PREF_MAP = {}
USER_PREF_MAP = {}

def generate_csv(ARTWORK_PREF_MAP, artwork_map):
    with open(ARTWORK_GALLERY_LIKES_DISLIKES_CSV_PATH, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('id', 'title', 'room', 'likes', 'dislikes'))
        for item_id, vals in ARTWORK_PREF_MAP.items():
            title = artwork_map[item_id]['title']
            room = artwork_map[item_id]['room']
            #writer.writerow((item_id, title.encode('utf-8'), room, vals['like'], vals['dislike']))
            writer.writerow((item_id, title, room, vals['like'], vals['dislike']))

def build_title_map():
    artwork_data = read_artwork_data(ARTWORK_CSV_PATH)
    title_map = {}
    for art in artwork_data:
        title_map[art['id']] = {'title': art['title'], 'room': art['room']}
    return title_map

def populate_maps(pref_data):
    # Prepopulate the map
    for pref in pref_data:
        ARTWORK_PREF_MAP[pref['item_id']] = {'like': 0, 'dislike': 0}

    for pref in pref_data:
        if pref['pref'] == 'True':
            ARTWORK_PREF_MAP[pref['item_id']]['like'] += 1
        else:
            ARTWORK_PREF_MAP[pref['item_id']]['dislike'] += 1


def main():

    pref_data = read_prefs_data(PREF_CSV_PATH, skip_admin_survey=False)
    print 'Read %s preferences from csv' % len(pref_data)

    title_map = build_title_map()
    populate_maps(pref_data)

    generate_csv(ARTWORK_PREF_MAP, title_map)

if __name__ == "__main__":
    main()