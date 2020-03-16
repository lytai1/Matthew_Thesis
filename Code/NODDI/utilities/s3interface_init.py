from s3_interface import S3Interface; import os; s3 = S3Interface(os.environ['AWS_S3_KEY'], os.environ['AWS_S3_PRIVATE_KEY'], 'cs-sjsu-noddi-patient-files');
