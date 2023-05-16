import pathlib
import pandas as pd
from rich.console import Console
from rich.table import Column, Table
from rich.progress import track
import argparse
import textwrap
import boto3
import json
import os
import glob
import tqdm
import configparser
import subprocess

config = configparser.ConfigParser()
config.read_file(open('confs/dpipe.cfg'))

KEY = config.get('AWS', 'ACCESS_KEY_ID')
SECRET = config.get('AWS', 'SECRET_ACCESS_KEY')
DL_CLUSTER_ID = config.get("CLUSTER", "ID")
IAM_ROLE_ARN = config.get("IAM_ROLE",  "ARN")
DL_IAM_ROLE_NAME = config.get("CLUSTER", "DL_IAM_ROLE_NAME")
DL_QUOTES_BUCKET_NAME = config.get("CLUSTER", "DL_QUOTES_BUCKET_NAME")
DL_OPTIONS_BUCKET_NAME = config.get("CLUSTER", "DL_OPTIONS_BUCKET_NAME")
DL_CODE_BUCKET_NAME = config.get("CLUSTER", "DL_CODE_BUCKET_NAME")
DL_DATA_BUCKET_NAME = config.get("CLUSTER", "DL_DATA_BUCKET_NAME")

def prettyEMRProps(props):
    l_data = [('Id', props['Id']),
              ('Name', props['Name']),
              ('State', props['Status']['State'])]

    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="dim", width=12)
    table.add_column("Value", justify="right")
    for row in l_data:
        table.add_row(
            *row
        )

    console.print(table)

def upload_files(s3, bucket_name, l_filepaths):
    try:
        response = s3.list_buckets()
        l_buckets = [bucket['Name'] for bucket in response['Buckets']]
        if bucket_name not in l_buckets:
            d_bucket_conf = {'LocationConstraint': 'us-west-2'}
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=d_bucket_conf)
            print(f'...create a new bucket with the name {bucket_name}')
        for s_filepath in track(l_filepaths):
            s_fname = s_filepath.split('/')[-1]
            s3.upload_file(s_filepath, bucket_name, s_fname)
    except Exception as e:
        print(e)
        return False
    return True

if __name__ == '__main__':
    s_txt = '''\
            Infrastructure as code
            --------------------------------
            Create Amazon EMR cluster and setup Airflow variables
            '''
    obj_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        formatter_class=obj_formatter, description=textwrap.dedent(s_txt))

    s_help = 'Create IAM role'
    parser.add_argument('-i', '--iam', action='store_true', help=s_help)

    s_help = 'Upload data to S3'
    parser.add_argument('-u', '--upload', action='store_true', help=s_help)

    s_help = 'Create a EMR cluster'
    parser.add_argument('-e', '--emr', action='store_true', help=s_help)

    s_help = 'Check EMR cluster status'
    parser.add_argument('-s', '--status', action='store_true', help=s_help)

    s_help = 'Run etl.py'
   
