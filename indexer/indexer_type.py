from enum import Enum


class IndexerType(Enum):
    GITHUB = {"id_prefix": "github", "code_hosting_queue": "github", "database_table": "github"}
    GITLAB = {"id_prefix": "gitlab", "code_hosting_queue": "gitlab", "database_table": "gitlab"}
    BITBUCKET = {"id_prefix": "bitbucket", "code_hosting_queue": "bitbucket", "database_table": "bitbucket"}
    SOURCEFORGE = {"id_prefix": "sourceforge", "code_hosting_queue": "sourceforge", "database_table": "sourceforge"}
    LAUNCHPAD = {"id_prefix": "launchpad", "code_hosting_queue": "launchpad", "database_table": "launchpad"}
    GNU_SAVANNAH = {"id_prefix": "gnu_savannah", "code_hosting_queue": "gnu_savannah", "database_table": "gnu_savannah"}
