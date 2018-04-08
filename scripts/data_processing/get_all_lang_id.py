"""
Get all language IDs for the data.
"""
import pandas as pd
import json
from langid import classify
from argparse import ArgumentParser

def get_lang_id(json_file):
    """
    Get most likely lang ID 
    for every valid status
    in json file.

    Parameters:
    -----------
    json_file : str
    
    Returns:
    --------
    lang_ids = pandas.DataFrame
    Rows = samples, columns = [status ID, lang ID, lang confidence]
    """
    lang_ids = []
    for l in open(json_file, 'r'):
        try:
            j = json.loads(l)
            if(j.get('text') is not None):
                j_id = j['id']
                j_txt = j['text']
                j_lang = classify(j_txt)
                j_lang, j_lang_conf = j_lang
                lang_ids.append([j_id, j_lang, j_lang_conf])
        except Exception, e:
            print('skipping status %s because exception %s'%(l, e))
    col_names = ['id', 'lang', 'conf']
    lang_ids = pd.DataFrame(lang_ids, columns=col_names)
    return lang_ids

def main():
    parser = ArgumentParser()
    parser.add_argument('--json_file', default='../../data/tweets/archive_Sep-30-16_Oct-31-17_ES_tweets.json')
    args = parser.parse_args()
    json_file = args.json_file
    
    ## get lang IDs
    lang_ids = get_lang_id(json_file)
    
    ## write to file
    out_file_name = json_file.replace('tweets.json', 'lang.tsv')
    print(out_file_name)
    lang_ids.to_csv(out_file_name, sep='\t', index=False)

if __name__ == '__main__':
    main()
