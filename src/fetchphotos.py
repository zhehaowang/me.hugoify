#! /usr/bin/env python3

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import urllib.request
import glob
import os
import logging
import hashlib

class GooglePhotosGetter():
    def __init__(self):
        self.service = None
        self.setup()

    def setup(self):
        SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('photoslibrary', 'v1', http=creds.authorize(Http()))

    def get_albums(self, page_size=50):
        results = self.service.albums().list(
            pageSize=page_size, fields="nextPageToken,albums(id,title)").execute()
        items = results.get('albums', [])
        if not items:
            logging.info('No albums found.')
        else:
            return items

    def filter_albums(self, items):
        return [x for x in items if x['title'].startswith("p_")]

    def get_photos(self, album_id, target_dir=None, page_size=50):
        # get album title
        album = self.service.albums().get(
            albumId=album_id).execute()
        title = album['title'].strip("p_")
        logging.info('working with album {}'.format(title))

        # get pics in album
        pics = self.service.mediaItems().search(body={
            "pageSize": page_size,
            "albumId": album_id
        }).execute()

        # to keep stuff in sync we only fetch the names not currently in
        # assuming when we overwrite stuff in google photos, we use a different name
        # @todo(zwang): should handle deletion!
        folder_name = os.path.join(target_dir, title)
        files = []
        file_hashes = []
        if os.path.exists(folder_name):
            files = list(glob.glob(os.path.join(folder_name, "*")))
            file_hashes = [hashlib.md5(open(f, 'rb').read()).hexdigest() for f in files]
            files = [os.path.basename(f) for f in files]
            logging.info("currently has files {}".format(files))
        else:
            os.makedirs(folder_name)
            logging.info("creating path {}".format(folder_name))
        
        for p in pics['mediaItems']:
            # crappy quality
            if p['filename'] in files:
                continue
            suffix = '=w1024' if p['mediaMetadata']['width'] > p['mediaMetadata']['height'] else '=h1024'
            download_url = p['baseUrl'] + suffix
            target_filename = os.path.join(folder_name, p['filename'])
            urllib.request.urlretrieve(download_url, target_filename)
            # unideal that we file io first then remove, but quick hack to not fetch renamed duplicates
            target_hash = hashlib.md5(open(target_filename, 'rb').read()).hexdigest()
            if target_hash in file_hashes:
                os.remove(target_filename)
            else:
                logging.info('populating {} from {}'.format(target_filename, download_url))
        return

    def run(self):
        albums = self.get_albums()
        filtered_albums = self.filter_albums(albums)
        for album in filtered_albums:
            self.get_photos(album['id'], "../generated/static/gallery")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    photos_getter = GooglePhotosGetter()
    photos_getter.run()
