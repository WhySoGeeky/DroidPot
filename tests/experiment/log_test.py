import logging,os

lg = logging.getLogger("test")
lg.setLevel(logging.INFO)
log_path = os.path.join("test.log")
fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
lg.addHandler(fh)

lg.info("wwwww")
