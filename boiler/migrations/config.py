import os
from alembic.config import Config as AlembicConfig


class MigrationsConfig(AlembicConfig):
    def __init__(self, path, db_url, metadata, *args, **kwargs):
        self.dir=path
        self.url=db_url
        self.meta=metadata
        self.config = os.path.join(self.dir, 'alembic.ini')

        # bootstrap with ini if exists
        initialized = os.path.isfile(self.config)
        if initialized:
            args = list(args)
            args.insert(0, self.config)

        super().__init__(*args, **kwargs)
        self.set_main_option('sqlalchemy.url', db_url)
        self.set_main_option('script_location', path)
        self.config_file_name = self.config

    def get_template_directory(self):
        """
        Get path to migrations templates
        This will get used when you run the db init command
        """
        dir = os.path.join(os.path.dirname(__file__), 'templates')
        return dir

