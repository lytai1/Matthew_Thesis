from dmipy.hcp_interface import downloader_aws
import logging
import argparse

logger = logging.getLogger(__name__)

def make_hcp_interface(public_key, secret_key):

	hcp_interface = downloader_aws.HCPInterface(
				your_aws_public_key=public_key,
				your_aws_private_key=private_key
			)
	return hcp_interface

def download_subject(interface, subject_id):
	
	logger.info(f"Downloading subject with id: {subject_id}")
	interface.download_subject(subject_ID=subject_id)
	logger.info(f"Finished downloading subject with id: {subject_id}")

def get_available_subjects(interface):

	available_subjects = str(interface.available_subjects)
	logger.info(f"Available subjects: {available_subjects}")


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Downloader interface')
	parser.add_argument('subject_id', 'id', type=string, help='the subject id to download the patient')
	parser.add_argument('get_subjects', type=bool, help='list the available subjects')

	args = parser.parse_args()
	
	hcp_interface = make_hcp_interface(os.env['HCP_PUBLIC_KEY'], os.env['HCP_PRIVATE_KEY'])
	if args.get_subjects:
		get_available_subjects(hcp_interface)


		
	
