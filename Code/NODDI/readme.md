S3 file upload example:

from s3_interface import S3Interface
import os

s3 = S3Interface(os.environ['AWS_S3_KEY'], os.environ['AWS_S3_PRIVATE_KEY'], 'cs-sjsu-noddi-patient-files')
s3.upload_files(os.path.join(os.environ['DATA_DIR'], os.path.join('021_S_2077','021_S_2077.pkl')), '/patients/ADNI/021_S_2077/021_S_2077.pkl')

