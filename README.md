# front-end-project-deployment-scripts
> 适合Vue前端(Docker部署Nginx)+SpringBoot后端(Jar包形式部署)。  
> 其他文件类型应该也可运行,不过仅可能做数据传输和文件夹清理，没法一键部署。  
> 如果不使用Docker或Docker中管理此项目的Nginx容器名不为"nginx，则同样需要你手动重启nginx。  
>  `如果你不是很熟悉手动部署, 建议先了解手动部署, 阅读:`

> 原理: 使用ssh执行bash + sftp传输文件    
> 使用方式:   
1. 你需要在yaml文件里配置服务器信息(服务器ip, ssh端口号(默认22), 用户名, 密码);
2. 前端文件夹名(vue为dist (通过npm run build得到)), 本地前端文件夹所在目录, 服务器前端文件夹所在目录;
3. 后端文件名(SpringBoot为xxx.jar), 后端文件所在目录, 服务器后端所在目录。   
