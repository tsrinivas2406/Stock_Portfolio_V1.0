import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')

# Create a logger
logger = logging.getLogger(__name__)


# The logs you're seeing for urllib3.connectionpool are due to the logging configuration's 
# DEBUG level, which captures debug logs from all modules, including third-party libraries. 
# If you want to restrict logging to only your application and exclude logs from other libraries, 
# you can adjust the logging configuration to filter out logs from specific libraries.
###################################################################################

# Set the logging level for `urllib3` to a higher level to suppress its debug logs
logging.getLogger('urllib3').setLevel(logging.WARNING)

# 2024-07-05 14:01:46,098 - PIL.PngImagePlugin - DEBUG - STREAM b'IHDR' 16 13
logging.getLogger('PIL').setLevel(logging.WARNING)