#!/usr/bin/env python

import boto3

BUCKET = "cloudnost"
FILE_NAME = "notetesting/wrote_string.txt"

#Creating Session With Boto3.
session = boto3.Session(
)

#Creating S3 Resource From the Session.
s3 = session.resource('s3')

txt_data = b'This is the content of the file uploaded from python boto3 asdfasdf'

object = s3.Object(BUCKET, FILE_NAME)

result = object.put(Body=txt_data)
