import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from parser.main import YandexMapsParser
    logger.debug("Successfully imported YandexMapsParser")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Python path: {sys.path}")
    raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--org_id', type=str, required=True,
                        help='''On the company page, the numbers in the address bar.
                        For example, for https://yandex.ru/maps/org/yandeks/1124715036/reviews/ we need 1124715036''')

    args = parser.parse_args()
    
    logger.info(f"Starting review extraction for organization ID: {args.org_id}")
    
    # Initialize parser and get reviews
    try:
        maps_parser = YandexMapsParser()
        maps_parser.get_organization_reviews(org_id=int(args.org_id))
        logger.info("Review extraction completed successfully")
    except Exception as e:
        logger.error(f"Error during review extraction: {e}")
        raise
