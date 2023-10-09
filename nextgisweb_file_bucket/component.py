import os.path

from nextgisweb.env import Component


class FileBucketComponent(Component):
    def initialize(self):
        self.path = self.env.core.gtsdir(self)

    def initialize_db(self):
        self.env.core.mksdir(self)

    def setup_pyramid(self, config):
        from . import api, view  # NOQA

        api.setup_pyramid(self, config)
        view.setup_pyramid(self, config)

    def dirname(self, stuuid, makedirs=False):
        levels = (stuuid[0:2], stuuid[2:4], stuuid)
        path = os.path.join(self.path, *levels)

        if makedirs and not os.path.isdir(path):
            os.makedirs(path)

        return path
