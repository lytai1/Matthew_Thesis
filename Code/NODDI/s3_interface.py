import boto
import os


class S3Interface:

	def __init__(self, public_key, secret_key, bucket_pattern):

		self.public_key = public_key
		self.secret_key = secret_key
		self.bucket_pattern = bucket_pattern

		s3 = boto.connect_s3(
			aws_access_key_id=self.public_key,
			aws_secret_access_key=self.secret_key
			)

		for key in s3.get_all_buckets():
			if key.name.find(self.bucket_pattern) != -1:
				self.s3_bucket = key
				break

		
