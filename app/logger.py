import logging
import re

# Any log message containing these field names has its value redacted. (LOG-3)
_SCRUB_RE = re.compile(
    r'(password|token|secret|key|authorization|credential)\s*[=:]\s*\S+',
    re.IGNORECASE,
)


class _ScrubFilter(logging.Filter):
    def filter(self, record):
        record.msg = _SCRUB_RE.sub(lambda m: m.group(0).split('=')[0] + '=[REDACTED]', str(record.msg))
        record.args = ()
        return True


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s]: %(message)s'
        ))
        handler.addFilter(_ScrubFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
