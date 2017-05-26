class Config:
    SECRET_KEY='jqleSv89245tl#=4gm;45gP54*/76542@'
    DEBUG = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+pypostgresql://xzizka:Passw0rd@10.11.78.140:5432/loganalyzer_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+pypostgresql://xzizka:Passw0rd@10.11.78.140:5432/loganalyzer_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+pypostgresql://xzizka:Passw0rd@10.11.78.140:5432/loganalyzer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

config_by_name = dict(
    dev = DevelopmentConfig,
    test = TestingConfig,
    prod = ProductionConfig
)