import os

import paramiko
import yaml


# 递归上传文件夹
def upload_folder(sftp, local_path, remote_path):
    sftp.mkdir(remote_path)
    for item in os.listdir(local_path):
        local_item_path = local_path + '/' + item
        remote_item_path = remote_path + '/' + item
        if os.path.isfile(local_item_path):
            sftp.put(local_item_path, remote_item_path)
        elif os.path.isdir(local_item_path):
            try:
                upload_folder(sftp, local_item_path, remote_item_path)
            except IOError as e:
                # 目标文件夹已存在
                print(e)
                pass


# 部署前端
def deploy_front_end(ssh, local_frontend_file_name, local_frontend_directory, target_frontend_directory):
    sftp = ssh.open_sftp()

    ssh.exec_command(r'mkdir ' + target_frontend_directory)  # 创建前端文件所在目录
    ssh.exec_command(r'rm -rf ' + target_frontend_directory + local_frontend_file_name)     # 移除旧前端文件夹
    upload_folder(sftp, local_frontend_directory + local_frontend_file_name, target_frontend_directory + local_frontend_file_name)  # 上传整个文件夹
    stdin, stdout, stderr = ssh.exec_command(r'docker restart nginx')   # 重启Docker的Nginx容器
    if stdout.read().decode() is None:
        print(stderr.read().decode())
        print('你需要在docker内运行配置好端口映射的nginx容器, 且容器名为nginx, 如果你不用容器可以直接在你的nginx里直接做配置')
    print(r'frontend deployed successfully')
    sftp.close()


# 部署后端
def deploy_back_end(ssh, local_backend_jar_name, local_backend_jar_location, target_backend_jar_location):
    sftp = ssh.open_sftp()

    ssh.exec_command(r'mkdir ' + target_backend_jar_location)   # 创建后端文件所在目录
    ssh.exec_command(
        r"kill -9 $(ps -ef | grep '" + local_backend_jar_name + "' | grep -v grep | awk '{print $2}')")  # 停止当前运行的后端进程
    ssh.exec_command(r'rm -f ' + target_backend_jar_location + local_backend_jar_name)  # 移除后端文件

    sftp.put(local_backend_jar_location + local_backend_jar_name, target_backend_jar_location + local_backend_jar_name)  # 上传后端单文件
    stdin, stdout, stderr = ssh.exec_command(r'nohup java -jar ' + target_backend_jar_location + local_backend_jar_name)  # 执行nohup java -jar

    if stderr.read().decode() is not None:
        print('[运行jar包时发生错误] 请手动在服务器执行:\nnohup java -jar ' + target_backend_jar_location + local_backend_jar_name)
        print(stderr.read().decode())
    else:
        print(r'backend deployed successfully')
    sftp.close()


if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)

    with open('./conf.yaml', 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    # ssh连接
    ssh.connect(
        hostname=config['hostname'],
        port=config['port'],
        username=config['username'],
        password=config['password']
    )
    # sftp连接

    choice = 1
    while choice:
        print('=========================FRONT-END-PROJECT-DEPLOYMENT-SCRIPTS==========================')
        print('!!!请注意: 前端适用于部署(传输)一整个文件夹, 而后端适用于传输一个单文件，每次重新部署时这两个文件都会被覆盖!!!')
        print('请输入: [1] 部署前端 [2] 部署后端 [0] 结束')
        choice = input()
        if choice == '1':
            deploy_front_end(ssh, config['local-frontend-file-name'], config['local-frontend-directory'], config['target-frontend-directory'])
        if choice == '2':
            deploy_back_end(ssh, config['local-backend-jar-name'], config['local-backend-jar-location'], config['target-backend-jar-location'])
        if choice == '0':
            break

    # 关闭SFTP客户端和SSH连接
    ssh.close()
