#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, tarfile
from datetime import datetime

# 导入Fabric API:
from fabric.api import *

# 服务器登录用户名和密钥
env.user = 'root'
env.sudo_user = 'root'
env.host_string = '47.102.156.80'
env.passwords = {'password': '031018@my@dream'}
env.key_filename = 'E:/myKey.pem'


# 服务器MySQL用户名和口令：
db_user = 'www-data'
db_password = 'www-data'
_TAR_FILE = 'dist-awesome.tar.gz'
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'


def _current_path():
    return os.path.abspath('.')


def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')


def build():
    # includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py', '*.txt']
    # excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('del dist\\%s' % _TAR_FILE) # 删除旧压缩包
    tar = tarfile.open("dist/%s" % _TAR_FILE, "w:gz") # 创建新压缩包
    for root, _dir, files in os.walk("www/"): # 打包www文件夹
        for f in files:
            if not (('.pyc' in f) or ('.pyo' in f)):
                fullpath = os.path.join(root, f)
                tar.add(fullpath)
    tar.close()



def deploy():
    newdir = 'www-%s' % _now()
    #删除已有的tar文件：
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件：
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录：
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    # 解压到新目录：
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR) # 解压
        sudo('mv www/* .') # 解压后多一层www文件夹，所以向上移动一层
        sudo('rm -rf www') # 删除空文件夹www
        sudo('dos2unix app.py') # 解决windows和linux行尾换行不同问题
        sudo('chmod a+x app.py') # 使app.py可以直接执行
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -rf www') # 删除旧软连接
        sudo('ln -s %s www' % newdir) # 创建新链接
        sudo('chown root www') # user改为linux服务器上的用户名
        sudo('chown -R root %s' % newdir) # 同上
        # 需要添加权限浏览器才能访问
        # sudo('chmod -R 775 static/')
        # sudo('chmod 775 favicon.ico')
        # # 由于app.py的文件格式有问题，转换一下
        # run('app.py')
    # 重启python服务和nginx服务器
    with settings(warn_only=True):
        sudo('supervisorctl stop awesome') #
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')


RE_FILES = re.compile('\r?\n')


def rollback():
    '''
    rollback to previous version
    '''
    with cd(_REMOTE_BASE_DIR):
        r = run('ls -p -1')
        files = [s[:-1] for s in RE_FILES.split(r) if s.startswith('www-') and s.endswith('/')]
        files.sort(reverse=True)
        r = run('ls -l www')
        ss = r.split(' -> ')
        if len(ss) != 2:
            print('ERROR: \'www\' is not a symbol link.')
            return
        current = ss[1]
        print('Found current symbol link points to: %s\n' % current)
        try:
            index = files.index(current)
        except ValueError as e:
            print('ERROR: symbol link is invalid.')
            return
        if len(files) == index + 1:
            print('ERROR: already the oldest version.')
        old = files[index + 1]


        print('=====================================================')
        for f in files:
            if f == current:
                print('      Current ---> %s' % current)
            elif f == old:
                print('  Rollback to ---> %s' % old)
            else:
                print('                   %s' % f)

        print('=====================================================')
        print('')
        yn = input('continue? Y/N ')
        if yn != 'y' and yn != 'Y':
            print('Rollback cancelled.')
            return
        print('Start rollback...')
        sudo('rm -f www')
        sudo('ln -s %s www' % old)
        sudo('chown www-data:www-data www')
        with settings(warn_only=True):
            sudo('supervisorctl stop awesome')
            sudo('supervisorctl start awesome')
            sudo('/etc/init.d/nginx reload')
        print('ROLLBACKED OK.')


def backup():
    '''
    Dump entire database on server and backup to local.
    '''
    dt = _now()
    f = 'backup-awesome-%s.sql' % dt
    with cd('/tmp'):
        run('mysqldump --user=%s --password=%s --skip-opt --add-drop-table --default-character-set=utf8 --quick awesome > %s' % (db_user, db_password, f))
        run('tar -czvf %s.tar.gz %s' % (f, f))
        get('%s.tar.gz' % f, '%s/backup/' % _current_path())
        run('rm -f %s' % f)
        run('rm -f %s.tar.gz' % f)


def restore2local():
    '''
    Restore db to local
    '''
    backup_dir = os.path.join(_current_path(), 'backup')
    fs = os.listdir(backup_dir)
    files = [f for f in fs if f.startswith('backup-') and f.endswith('.sql.tar.gz')] # 获取备份文件列表
    files.sort(reverse=True) # 最近的文件排在前面
    if len(files) == 0:
        print('No backup files found.')
        return
    print('Found %s backup files:' % len(files))
    print('====================================================')
    n = 0
    for f in files:
        print('%s: %s' % (n, f))
        n = n + 1
    print('====================================================')
    print('')
    try:
        num = int(input ('Restore file: ')) # 选择恢复哪个备份
    except ValueError:
        print('Invalid file number.')
        return
    restore_file = files[num]
    yn = input('Restore file %s: %s? y/N ' % (num, restore_file))
# 确定开始恢复
    if yn != 'y' and yn != 'Y':
        print('Restore cancelled.')
        return
    print('Start restore to local database...')
    p = input('Input mysql root password: ')
    sqls = [
        'drop database if exists awesome;',
        'create database awesome;',
        'alter database awesome default character set utf8 collate utf8_general_ci;' # 修改为utf8字符集
        'grant select, insert, update, delete on awesome.* to \'%s\'@\'localhost\' identified by \'%s\';' % (db_user, db_password)
    ]
    for sql in sqls:
        local(r'mysql -uroot -p%s -e "%s"' % (p, sql)) # 删除旧数据库，新建数据库，授权给用户
    extract('backup\\%s' %restore_file, 'backup\\') # 解压
    with lcd('backup'):
    # linux系统和windows系统之间数据库导入导出可能会因为字符集不同出现’unknown command \\'错误
    # 通过在创建数据库后修改为utf8字符集，以及导入时指定--default-character-set=utf8,解决这个问题
        local(r'mysql -uroot -p%s --default-character-set=utf8 awesome < %s' % (p, restore_file[:-7])) # 导入数据库
        local('del %s' % restore_file[:-7]) # 删除解压出的文件


def extract(tar_path, target_path):
    '''
    解压tar.gz文件到目标目录
    '''
    try:
        tar = tarfile.open(tar_path, "r:gz")
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, target_path)
        tar.close()
    except Exception as e:
        raise e

if __name__ == '__main__':
    build()
    deploy()
    # rollback()
    # backup()
    # restore2local()
    input()


