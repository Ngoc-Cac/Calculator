import os.path as osp

import logging

cur_dir = osp.dirname(__file__)
log_dir = "logs"

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set corresponding level
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_file = ["debug.log", "info.log", "warning.log", "error.log"]
log_level = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
for file, level in zip(log_file, log_level):
    fh = logging.FileHandler(osp.join(cur_dir, log_dir, file))
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logging.basicConfig(filename=osp.join(cur_dir, log_dir, "debug.log"), level=logging.DEBUG)

try:
    import main_tasks
    logger.info("Program started successfully")
    main_tasks.main_tasks()
    logger.info("Program exitted successfully")
except Exception as e:
    logger.debug(e, exc_info=True)