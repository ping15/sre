import pymysql
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'migrate迁移文件，如果数据库不存在将自动创建'

    def handle(self, *args, **kwargs):
        self.ensure_database_exists()
        call_command('migrate')

    def ensure_database_exists(self):
        db_config = settings.DATABASES['default']

        try:
            conn = pymysql.connect(
                host=db_config['HOST'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                port=int(db_config['PORT'])
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_config['NAME']}` "
                           f"DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;")
            cursor.close()
            conn.close()
        except pymysql.MySQLError as e:
            raise CommandError(f"Error creating database: {e}")

        self.stdout.write(self.style.SUCCESS(f"Database '{db_config['NAME']}' ensured to exist."))
