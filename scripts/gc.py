#!/usr/bin/env python3

import fire
import json
import os

LANGS = {1: 'JPN', 2: 'ENG', 3: 'FRA', 4: 'ITA', 5: 'GER', 7: 'SPA', 8: 'KOR', 9: 'CHS', 10: 'CHT'}

class Main(object):
    def process_raw(self, input_dir, output_file):
        print('Processing raw data from', input_dir)
        filelist = os.listdir(input_dir)
        data = []
        for filename in filelist:
            print('Processing', filename)
            with open(os.path.join(input_dir, filename), 'r') as f:
                data.extend(json.load(f))
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

    def _print_player(self, player, file):
        region_rank = player.get('jp_rank') or player.get('kr_rank') or player.get('tpci_rank')
        rating = player['rating_value'] / 1000
        print(region_rank, player['rank'], player['name'], rating, sep='\t', file=file)

    def report(self, input_file):
        with open(input_file, 'r') as f:
            data = json.load(f)
        print('Total players:', len(data))
        jp_players = [x for x in data if x.get('jp_rank')]
        print()
        print('Japanese players:', len(jp_players))
        print('Japanese rank 1-3:')
        for i in range(3):
            self._print_player(jp_players[i])
        print('Japanese rank 150:')
        self._print_player(jp_players[149])

        kr_players = [x for x in data if x.get('kr_rank')]
        print()
        print('Korean players:', len(kr_players))
        print('Korean rank 1-3:')
        for i in range(3):
            self._print_player(kr_players[i])
        print('Korean rank 50:')
        self._print_player(kr_players[49])

        print()
        tpci_players = [x for x in data if x.get('tpci_rank')]
        print('TPCi players (assuming all others are in the TPCi region):', len(tpci_players))
        for rank in [1,2,3,4,8,16,32,64,128,256,512,1024]:
            self._print_player(tpci_players[rank-1])

    def report_langs(self, input_file, output_dir):
        with open(input_file, 'r') as f:
            data = json.load(f)
        os.makedirs(output_dir, exist_ok=True)
        for lang_i, lang in LANGS.items():
            print(f'Processing {lang}')
            with open(os.path.join(output_dir, f'{lang}.tsv'), 'w') as f:
                print('RegionRank', 'Rank', 'Name', 'Rating', sep='\t', file=f)
                for each in data:
                    if each['lng'] == lang_i:
                        self._print_player(each, file=f)
        print('Data saved to', output_dir)

if __name__ == '__main__':
    fire.Fire(Main)
