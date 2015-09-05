from fabric.api import env

import build  # noqa
import check  # noqa
try:
    import deploy  # noqa
except ImportError:
    pass

env.use_ssh_config = True
