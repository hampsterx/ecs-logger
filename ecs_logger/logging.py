import logging
import os
import json
import traceback
from ecs_logger.ecs_meta import read_ecs_meta
from datetime import datetime

_ecs_meta = None

class ECSJSONLogFormatter(logging.Formatter):

    ecs_meta = None

    def __init__(self, ecs_meta=None):

        self.ecs_meta = ecs_meta


    def format(self, record):
        obj = {
            "@timestamp": datetime.utcnow().isoformat(),
            "message": record.getMessage(),
            "tags": [],
            "log.thread": record.threadName,
            "log.level": record.levelname,
            "log.line_no": record.lineno,
            "log.name": record.name,
            "log.filename": record.filename,
            "log.module": record.module

        }

        if hasattr(record, 'props'):
            obj.update(record.props)

        if self.ecs_meta:
            obj.update(self.ecs_meta)
            # Convenience
            obj['tags'].append(self.ecs_meta['cloud.cluster'])
            # Convenience
            obj['tags'].append(self.ecs_meta['service.name'])

        fields = record.__dict__.copy()

        keys = ['name', 'msg', 'args', 'levelname', 'lineno', 'funcName',
                'created', 'relativeCreated','msecs', 'threadName','process',
                'processName', 'levelno', 'pathname', 'filename', 'module',
                'thread', 'exc_text', 'stack_info'
                ]

        [fields.pop(k) for k in keys]

        if 'exc_info' in fields and fields['exc_info']:
            if fields['exc_info']:
                obj['exception.name'] = fields['exc_info'][0].__name__
                obj['exception.traceback'] = traceback.format_exception(*fields['exc_info'])

        fields.pop('exc_info')

        obj['data'] = fields


        return json.dumps(obj)



def configure_logging():

    is_json_logging = os.environ.get('JSON_LOGGING', None) == 'true'
    is_verbose = os.environ.get('VERBOSE_LOGGING', None) == 'true'

    level = logging.DEBUG if is_verbose else logging.INFO

    log_handler = logging.StreamHandler()

    if is_json_logging:
        ecs_meta = read_ecs_meta()
        log_handler.setFormatter(ECSJSONLogFormatter(ecs_meta=ecs_meta))

    else:
        from coloredlogs import ColoredFormatter
        log_handler.setFormatter(ColoredFormatter(fmt='%(name)s %(levelname)s %(message)s'))

    # replace root logging
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers = [log_handler]


def get_logger(name, level=None):

    log = logging.getLogger(name)
    if level:
        log.setLevel(level)

    return log
