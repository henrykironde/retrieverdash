import json
import os
from multiprocessing import Pool

from filelock import FileLock
from retriever import datasets

from status_dashboard_tools import (
    get_dataset_md5,
    diff_generator,
    create_dirs,
    dataset_to_csv)

file_location = os.path.dirname(os.path.realpath(__file__))

example_datasets = ['airports', 'gdp', 'portal', 'bird-size',
                    'aquatic-animal-excretion', 'prism-climate']

try:
    dataset_detail = json.load(open('dataset_details.json', 'r'))
except IOError:
    with open("dataset_details.json", 'w') as json_file:
        dataset_detail = dict()
        json.dump(dataset_detail, json_file)


def check_dataset(dataset):
    os.chdir(os.path.join(file_location))
    md5 = None
    status = None
    try:
        md5 = get_dataset_md5(dataset)
        if dataset.name not in dataset_detail or md5 != dataset_detail[
                dataset.name]['md5']:
            os.chdir(os.path.join(file_location, 'current'))
            dataset_to_csv(dataset)
            diff_generator(dataset)
        status = True
    except Exception as e:
        print(e)
        status = False
    finally:
        os.chdir(os.path.join(file_location))
        with FileLock('dataset_details.json.lock'):
            dataset_details_read = open('dataset_details.json', 'r')
            json_file_details = json.load(dataset_details_read)
            json_file_details[dataset.name] = {"md5": md5, "status": status}
            dataset_details_write = open('dataset_details.json', 'w')
            json.dump(json_file_details, dataset_details_write,
                      sort_keys=True, indent=4)


if __name__ == '__main__':
    create_dirs()
    pool = Pool(processes=3)
    pool.map(check_dataset, [dataset for dataset in datasets()
                             if dataset.name in example_datasets])
