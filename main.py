from app.app import create_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == '__main__':
    app = create_app()
    logger.info('Starting Flask development server')
    app.run(host='0.0.0.0', debug=True)
