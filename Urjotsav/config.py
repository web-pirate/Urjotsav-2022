class Config:
    SECRET_KEY = '2f14f2997d0cb0ac2fd939f11c8d38f074139fde1fcaa84c86d2c29199669d4976bb0ac05e48ec817c10c7637930af700a6a'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/tejearning'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///urjotsav.db'
    APP_Id = 'cf0100117d'
    APP_SECRET = '53de360c128a7f185c57e5a675a1404a90527ed6e997d789cc92985d01861684'

    # Mail Settings
    MAIL_SERVER = 'main.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'email@piemr.edu.in'
    MAIL_PASSWORD = 'password'
