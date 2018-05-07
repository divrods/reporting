import csv

def read_prefs_data(path, skip_admin_survey=True):
    return_objects = []
    with open(path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_num = 0
        for row in csvreader:
            row_num += 1

            # Skip Header
            if row_num == 1:
                continue  # header

            # Conditionally Skip admin survey
            if skip_admin_survey and row[1].startswith('admin_survey'):
                continue

            return_objects.append(
                {
                    'resource_id': row[0],
                    'user_id': row[1],
                    'item_id': row[2],
                    'pref': row[3],
                    'synced_timestamp': row[4],
                    'timestamp': row[5],
                    'occurances': 0,
                    'total_likes': 0
                })
    return return_objects


def read_artwork_data(path):
    return_objects = []
    with open(path, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        row_num = 0
        for row in csvreader:
            row_num += 1

            # Skip Header
            if row_num == 1:
                continue  # header

            return_objects.append(
                {
                    'id': row[0],
                    'title': row[1],
                    'artist': row[2],
                    'room': row[3],
                })
    return return_objects