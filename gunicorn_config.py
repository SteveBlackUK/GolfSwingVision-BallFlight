import os

bind = "0.0.0.0:8000"
workers = os.cpu_count() * 2 + 1
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" worker=%(p)s'
