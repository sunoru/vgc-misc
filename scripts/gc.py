#!/usr/bin/env python3

import csv
import json
import os
import requests

import fire

LANGS = {1: 'JPN', 2: 'ENG', 3: 'FRA', 4: 'ITA', 5: 'GER', 7: 'SPA', 8: 'KOR', 9: 'CHS', 10: 'CHT'}


def print_player(player, writer=None):
    region_rank = player.get('jp_rank') or player.get('kr_rank') or player.get('tpci_rank')
    rating = player['rating_value'] / 1000
    if writer is None:
        print(region_rank, player['rank'], player['name'], rating, sep='\t')
    else:
        writer.writerow([region_rank, player['rank'], player['name'], rating])

class Main(object):
    # API includes a %d for page number
    def download_data(self, api, max_page, output_file):
        print('Processing raw data from', api)
        data = []
        for page in range(1, max_page + 1):
            print('Processing Page', page)
            try:
                p = requests.get(api % page).json()
                data.extend(p)
            except Exception as e:
                print('Error: ', e)
                break
        data.sort(key=lambda x: x['rank'])
        jp_rank = 0
        kr_rank = 0
        tpci_rank = 0
        for each in data:
            del each['icon']
            lang = each['lng'] = int(each['lng'])
            match LANGS[lang]:
                case 'JPN':
                    jp_rank += 1
                    each['jp_rank'] = jp_rank
                case 'KOR':
                    kr_rank += 1
                    each['kr_rank'] = kr_rank
                case _:
                    tpci_rank += 1
                    each['tpci_rank'] = tpci_rank
        with open(output_file, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
        print('Data saved to', output_file)

    def report(self, input_file):
        with open(input_file, 'r') as f:
            data = json.load(f)
        print('Total players:', len(data))
        jp_players = [x for x in data if x.get('jp_rank')]
        print()
        print('Japanese players:', len(jp_players))
        print('Japanese rank 1-3:')
        for i in range(3):
            print_player(jp_players[i])
        print('Japanese rank 150:')
        print_player(jp_players[149])

        kr_players = [x for x in data if x.get('kr_rank')]
        print()
        print('Korean players:', len(kr_players))
        print('Korean rank 1-3:')
        for i in range(3):
            print_player(kr_players[i])
        print('Korean rank 50:')
        print_player(kr_players[49])

        print()
        tpci_players = [x for x in data if x.get('tpci_rank')]
        print('TPCi players (assuming all others are in the TPCi region):', len(tpci_players))
        for rank in [1,2,3,4,8,16,32,64,128,256,512,1024]:
            print_player(tpci_players[rank-1])

    def report_langs(self, input_file, output_dir):
        with open(input_file, 'r') as f:
            data = json.load(f)
        os.makedirs(output_dir, exist_ok=True)
        for lang_i, lang in LANGS.items():
            print(f'Processing {lang}')
            with open(os.path.join(output_dir, f'{lang}.tsv'), 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['Region Rank', 'Rank', 'Name', 'Rating'])
                for each in data:
                    if each['lng'] == lang_i:
                        print_player(each, writer=writer)
        print('Data saved to', output_dir)

if __name__ == '__main__':
    fire.Fire(Main)
