%define _user www
%define _group www
%define _prefix /data/lemp/php-5.6.31

Name: php
Version: 5.6.31
Release: 1%{?dist}
Summary: PHP is a server-side scripting language for creating dynamic Web pages

Group: Development/Languages
License: GPLv2
URL: http://www.php.net
Packager: eric <xiaozhk@gmail.com>
Source0: %{name}-%{version}.tar.gz
Source1: php-fpm.conf.default
Source2: php.ini.production
Source3: www.conf.default
BuildRoot: %_topdir/BUILDROOT

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
Requires: libiconv

%description
这是一个私人定制的PHP安装包，目录安装在/data/lemp/php-5.6.31

%prep
%setup -q

%build
./configure --prefix=%{_prefix} \
--with-config-file-path=%{_prefix}/etc \
--with-libdir=lib64 \
--enable-fpm \
--with-fpm-user=www \
--with-fpm-group=www \
--enable-mysqlnd \
--with-mysql=mysqlnd \
--with-mysqli=mysqlnd \
--with-pdo-mysql=mysqlnd \
--enable-opcache \
--enable-pcntl \
--enable-mbstring \
--enable-soap \
--enable-zip \
--enable-calendar \
--enable-bcmath \
--enable-exif \
--enable-ftp \
--enable-intl \
--with-openssl \
--with-zlib \
--with-curl \
--with-gd \
--with-zlib-dir=/usr/lib \
--with-png-dir=/usr/lib \
--with-jpeg-dir=/usr/lib \
--with-gettext \
--with-mhash \
--with-ldap

make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make INSTALL_ROOT=%{buildroot} install
rm -rf %{buildroot}/{.channels,.depdb,.depdblock,.filemap,.lock,.registry}
%{__install} -p -D -m 0755 sapi/fpm/init.d.php-fpm %{buildroot}/etc/init.d/php-fpm56
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}/%{_prefix}/etc/php-fpm.conf
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}/%{_prefix}/etc/php.ini
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}/%{_prefix}/etc/php-fpm.d/www.conf

%pre
echo '/usr/local/lib' > /etc/ld.so.conf.d/local.conf
/sbin/ldconfig
if [ $1 == 1 -a -z "`grep ^%{_user} /etc/passwd`" ]; then
    groupadd %{_group} -g 10000
    useradd -u 10000 -g 10000 -m %{_user}
fi


%post
if [ $1 == 1 ];then
    [ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=%{_prefix}/bin:\$PATH" >> /etc/profile
    [ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep '%{_prefix}' /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=%{_prefix}/bin:\1@" /etc/profile
    /sbin/chkconfig --add php-fpm56
    /sbin/chkconfig php-fpm56 on
    mkdir -p /tmp/{sock,session,upload}/php56
    chown -R %{_user}:%{_group} /tmp/{sock,session,upload}
fi



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


%postun 
if [ $1 == 0 ];then
    rm -f /etc/init.d/php-fpm56 > /dev/null 2>&1
    rm -rf ${_prefix} > /dev/null 2>&1
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_prefix}
%attr(0755,root,root) /etc/init.d/php-fpm56


%changelog
* Mon Sep 18 2017 eric <xiaozhk@gmail.com> 5.6.31-1
- Initial version

