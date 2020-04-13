1.更换国内的yum源
yum -y install wget
1)备份原来自带的yum源
cd /etc/yum.repos.d && mkdir backup && mv ./* ./backup

2)下载国内yum源和epel
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.163.com/.help/CentOS7-Base-163.repo
mv /etc/yum.repos.d/CentOS7-Base-163.repo /etc/yum.repos.d/CentOS-Base.repo

3)更新缓存
yum clean all 
yum makecache

2.安装常用工具
yum install ntpdate lsof net-tools gcc gcc-c++ make mtr nethogs iftop lrzsz vim openssh* psmisc openssl* ncurses ncurses-devel -y


安装最新版的sysstat
cd /usr/local/src
wget http://ftp5.gwdg.de/pub/linux/archlinux/community/os/x86_64//sysstat-12.1.5-1-x86_64.pkg.tar.xz
 （http://pagesperso-orange.fr/sebastien.godard/sysstat-12.2.0.tar.gz）
tar xf sysstat-12.1.5-1-x86_64.pkg.tar.xz
cp /usr/local/src/usr/bin/* /usr/bin

测试使用：
pidstat -d 1  ##老版本没有io的延迟iodelay，新版本有
pidstat -d 1 ##也多了好多


3.系统时间同步
EDT：指美国东部夏令时间
EST：英国时间
CST：北京时间
##如果时间为EST；需要先将时区改为CST
[root@localhost ~]# mv /etc/localtime /etc/localtime.bak
[root@localhost ~]# ln -s /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime
[root@localhost ~]# date

ntpdate cn.pool.ntp.org
echo '*/30 * * * * /usr/sbin/ntpdate cn.pool.ntp.org && hwclock -w && hwclock --systohc >/dev/null 2>&1' >> /var/spool/cron/root
systemctl restart crond

3. 调整文件描述符大小
echo -e "* soft nofile 65536 \n* hard nofile 65536 \n* soft nproc 65536 \n* hard nproc 65536" >> /etc/security/limits.conf
ulimit -SHn 65536 && ulimit -s 65536

4.锁定文件关键系统
chattr +i /etc/passwd 
chattr +i /etc/inittab 
chattr +i /etc/group 
chattr +i /etc/shadow 
chattr +i /etc/gshadow

5.配置history命令显示
在/etc/profile文件最后加两行：
USER_IP=`who -u -m | awk '{print $NF}'| sed 's/[()]//g'`
export HISTTIMEFORMAT="[%F %T][`whoami`][${USER_IP}] "
或者开启审计功能
采用以下步骤配置用户命令日志审计功能：
1.创建用户审计文件存放目录和审计日志文件 ； 
mkdir -p /var/log/usermonitor/
2.创建用户审计日志文件；
echo usermonitor >/var/log/usermonitor/usermonitor.log
3.将日志文件所有者赋予一个最低权限的用户；
chown nobody:nobody /var/log/usermonitor/usermonitor.log
4.给该日志文件赋予所有人的写权限； 
chmod 002 /var/log/usermonitor/usermonitor.log
5.设置文件权限,使所有用户对该文件只有追加权限 ；
chattr +a /var/log/usermonitor/usermonitor.log
6.编辑vim /etc/profile文件，添加如下脚本命令；
export HISTORY_FILE=/var/log/usermonitor/usermonitor.log
export PROMPT_COMMAND='{ date "+%y-%m-%d %T ##### $(who am i |awk "{print \$1\" \"\$2\" \"\$5}") #### $(whoami) #### $(history 1 | { read x cmd; echo "$cmd"; })"; } >>$HISTORY_FILE'
7.使配置生效
source /etc/profile
审计时查看/var/log/usermonitor/usermonitor.log文件即可，它会记录登上服务器所有用户使用的命令。为了更安全，还可以将改文件打包压缩，ftp至其它本地。
source /etc/profile


新建用户并配置sudo权限:
 useradd admin  
 passwd admin
  
 root	ALL=(ALL) 	ALL
 admin	ALL=(ALL) 	NOPASSWD:ALL  ##新增；此时admin用户可以直接使用sudo kill命令，不需要输入root密码。若需要输入root密码则格式为:admin	ALL=(ALL) 	ALL



6.tcp快速回收
cp /etc/sysctl.conf /etc/sysctl.conf.default
fs.file-max = 51200   #提高整个系统的文件限制
net.ipv4.tcp_syncookies = 1  #表示开启SYN Cookies。当出现SYN等待队列溢出时，启用cookies来处理，可防范少量SYN攻击，默认为0，表示关闭；
net.ipv4.tcp_tw_reuse = 1  #表示开启重用。允许将TIME-WAIT sockets重新用于新的TCP连接，默认为0，表示关闭；
net.ipv4.tcp_tw_recycle = 0 ##表示开启TCP连接中TIME-WAIT sockets的快速回收，默认为0，表示关闭；为了对NAT设备更友好，建议设置为0
net.ipv4.tcp_fin_timeout = 30 #修改系統默认的 TIMEOUT 时间。
net.ipv4.tcp_keepalive_time = 1200  #表示当keepalive起用的时候，TCP发送keepalive消息的频度。缺省是2小时，改为20分钟。
net.ipv4.ip_local_port_range = 10000 65000 #表示用于向外连接的端口范围。缺省情况下很小：32768到61000;若出现Cannot assign requested address这个报错，则需要增加这个值来缓解，例如1024 65535
net.ipv4.tcp_max_syn_backlog = 8192 #表示SYN队列的长度，默认为1024，加大队列长度为8192，可以容纳更多等待连接的网络连接数。
net.ipv4.tcp_max_tw_buckets = 5000 #表示系统同时保持TIME_WAIT的最大数量，如果超过这个数字，TIME_WAIT将立刻被清除并打印警告信息。


netstat -ant |grep '^tcp' |awk '{print $NF}' |sort |uniq -c |sort -rn
