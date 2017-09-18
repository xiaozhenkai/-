# 准备工作
## 安装rpm-build
`yum -y install rpm-build`
## 建立工作车间
```
useradd xiaozhenkai; su - xiaozhenkai
cat >  ~/.rpmmacros << EOF
%_topdir /home/xiaozhenkai/rpmbuild
EOF

mkdir -pv ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
```

>BUILD：源代码解压以后放的位置
>RPMS：制作完成后的rpm包存放目录，为特定平台指定子目录（x86_64）
>SOURCES：收集的源文件，源材料，补丁文件等存放位置
>SPECS：存放spec文件，作为制作rpm包的领岗文件，以rpm名.spec
>SRPMS：src格式的rpm包位置 ，既然是src格式的包，就没有平台的概念了
>BuiltRoot：假根，使用install临时安装到这个目录，把这个目录当作根来用的，所以在这个目录下的目录文件，才是真正的目录文件。当打包完成后，在清理阶段，这个目录将被删除

工作车间目录
`rpmbuild --showrc | grep topdir`
rpmbuild --showrc显示所有的宏，以下划线开头，一个下划线：定义环境的使用情况，二个下划线：通常定义的是命令，为什么要定义宏，因为不同的系统，命令的存放位置可能不同，所以通过宏的定义找到命令的真正存放位置


## 收集源码文件脚本文件
```
cd ~/rpmbuild/SOURCES
ls
php-5.6.31.tar.gz php-fpm.conf.default php.ini-production www.conf.default
```
##编写SPEC文件
`vim php.spec`
内容如下：
```
%define _user www
%define _group www
%define _prefix /data/lemp/php-5.6.31

Name: php  #软件包名称
Version: 5.6.31  #版本号（不能使用-）
Release: 1%{?dist}   #release号，对应下面的changelog，如php-5.6.31-1.el6.x86_64.rpm
Summary: PHP is a server-side scripting language for creating dynamic Web pages  #简要描述信息，最好不要超过50个字符，如要详述，使用下面的%description

Group: Development/Languages   #要全用这里面的一个组：less /usr/share/doc/rpm-version/GROUPS
License: GPLv2  #软件授权方式
URL: http://www.php.net  #源码相关网站
Packager: eric <xiaozhk@gmail.com>  #打包人的信息
Source0: %{name}-%{version}.tar.gz  #源代码包，可以带多个用Source1、Source2等源，后面也可以用%{source1}、%{source2}引用
Source1: php-fpm.conf.default
Source2: php.ini.production
Source3: www.conf.default
BuildRoot: %_topdir/BUILDROOT  #安装或编译时使用的"虚拟目录"

Requires: libxml2-devel
Requires: openssl-devel
Requires: libcurl-devel
Requires: libjpeg-turbo-devel
Requires: libpng-devel
Requires: libicu-devel
Requires: openldap-devel
Requires: libmcrypt
Requires: mhash
Requires: mcrypt
Requires: libiconv #定义php依赖的包，需要yum安装(此处使用epel源)

%description  #软件包详述
这是一个私人定制的PHP安装包，目录安装在/data/lemp/php-5.6.31

%prep  #软件编译之前的处理，如解压
%setup -q  #这个宏的作用静默模式解压并cd

%build  #开始编译软件
%configure \
--prefix=%{_prefix} \
--with-config-file-path=%{_prefix}/etc \
--with-fpm-user=%{_user} \
--with-fpm-group=%{_group} \
--enable-fpm \
--enable-fileinfo \
--with-mysql=mysqlnd \
--with-mysqli=mysqlnd \
--with-pdo-mysql=mysqlnd \
--with-iconv-dir=/usr/local \
--with-freetype-dir \
--with-jpeg-dir \
--with-png-dir \
--with-zlib \
--with-libxml-dir=/usr \
--enable-xml \
--disable-rpath \
--enable-bcmath \
--enable-shmop \
--enable-exif \
--enable-sysvsem \
--enable-inline-optimization \
--with-curl \
--enable-mbregex \
--enable-inline-optimization \
--enable-mbstring \
--with-mcrypt \
--with-gd \
--enable-gd-native-ttf \
--with-openssl \
--with-mhash \
--enable-pcntl \
--enable-sockets \
--with-xmlrpc \
--enable-ftp \
--enable-calendar \
--with-gettext \
--enable-zip \
--enable-soap \
--disable-ipv6 \
--disable-debug

make %{?_smp_mflags}
#%{?_smp_mflags} 的意思是：如果就多处理器的话make时并行编译

%install  #开始安装软件，如make install
rm -rf %{buildroot}
make INSTALL_ROOT=%{buildroot} install
rm -rf %{buildroot}/{.channels,.depdb,.depdblock,.filemap,.lock,.registry}
%{__install} -p -D -m 0755 sapi/fpm/init.d.php-fpm %{buildroot}/etc/init.d/php-fpm56
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}/%{_prefix}/etc/php-fpm.conf
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}/%{_prefix}/etc/php.ini
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}/%{_prefix}/etc/php-fpm.d/www.conf

#rpm安装前执行的脚本
%pre
echo '/usr/local/lib' > /etc/ld.so.conf.d/local.conf
/sbin/ldconfig
if [ $1 == 1 -a -z "`grep ^%{_user} /etc/passwd`" ]; then    # $1有3个值，代表动作，安装类型，处理类型
    groupadd %{_group} -g 10000                              # 1：表示安装
    useradd -u 10000 -g 10000 -m %{_user}                    # 2：表示升级
fi                                                           # 0：表示卸载

#rpm安装后执行的脚本
%post
if [ $1 == 1 ];then
    [ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=%{_prefix}/bin:\$PATH" >> /etc/profile
    [ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep '%{_prefix}' /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=%{_prefix}/bin:\1@" /etc/profile
    /sbin/chkconfig --add php-fpm56
    /sbin/chkconfig php-fpm56 on
    mkdir -p /tmp/{sock,session,upload}/php56
    chown -R %{_user}:%{_group} /tmp/{sock,session,upload}
fi


#rpm卸载前执行的脚本
%preun
if [ $1 == 0 ];then
    /etc/init.d/php-fpm56 stop > /dev/null 2>&1
    /sbin/chkconfig --del php-fpm56
    if [ -e '/etc/profile.d/custom_profile_new.sh' ];then
        sed -i 's@%{_prefix}/bin:@@' /etc/profile.d/custom_profile_new.sh
    else
        sed -i 's@%{_prefix}/bin:@@' /etc/profile
    fi
fi

#rpm卸载后执行的脚本
%postun 
if [ $1 == 0 ];then
    rm -f /etc/init.d/php-fpm56 > /dev/null 2>&1
    rm -rf ${_prefix} > /dev/null 2>&1
fi

%clean    #clean的主要作用就是删除BUILD
rm -rf %{buildroot}

%files  #指定哪些文件需要被打包，如/usr/local/php
%defattr(-,root,root,-)
%{_prefix}
%attr(0755,root,root) /etc/init.d/php-fpm56


%changelog  #日志改变段， 这一段主要描述软件的开发记录
* Mon Sep 18 2017 eric <xiaozhk@gmail.com> 5.6.31-1
- Initial version

```

## 编译rpm包
`rpmbuild -bb php.spec` 制作php rpm二进制包
`pmbuild -bb php-redis.spec` 制作php-redis rpm二进制包