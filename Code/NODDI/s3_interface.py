import boto3
import boto
import os
import logging
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3Transfer


class S3Interface:

	def __init__(self, public_key, secret_key, bucket_pattern):

		self.public_key = public_key
		self.secret_key = secret_key
		self.bucket_pattern = bucket_pattern

		self.transfer = S3Transfer(
				boto3.client('s3', 'us-east-1',
					aws_access_key_id=self.public_key,
					aws_secret_access_key=self.secret_key
				)
			  )
		self.s3 = boto.connect_s3(
				aws_access_key_id=self.public_key,
				aws_secret_access_key=self.secret_key
			  )	
		for key in self.s3.get_all_buckets():
			if key.name.find(self.bucket_pattern) != -1:
				self.s3_bucket = key
				self.bucket_name = key.name
				break

	def upload_file(self, file_path, destination_path):
	
		# based on the file path of the local directory, the bucket name found 
		# through th bucket_pattern, and the actual file from the file path
		try:
			self.transfer.upload_file(file_path, self.bucket_name, destination_path)
		except ClientError as e:
			logging.error(e)
			return False
		return True
