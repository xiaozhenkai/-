%define _user www
%define _group www
%define _prefix /data/lemp/php-5.6.31

Name: php		
Version: 5.6.31	
Release: 1%{?dist}
Summary: PHP 5.6 for xiaozhenkai	

Group: Applications/Internet
License: GPLv2
URL: http://xiaozhenkai.blog.51cto.com	
Source0: http://cn2.php.net/distributions/%{name}-%{version}.tar.gz
Source1: init.d.php-fpm
Source2: php-fpm.conf
Source3: php.ini-production
Source4: www.conf.default
BuildRequires: gcc, gcc-c++
Requires: libxml2-devel,openssl-devel,libcurl-devel,libjpeg-turbo-devel,libpng-devel,libicu-devel,openldap-devel

%description
PHP Compile Install

%prep
%setup -q


%build
./configure \
--prefix=%{_prefix} \
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
%{__install} -p -d -m 0755 %{buildroot}/data/lemp/
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}/etc/rc.d/init.d/php-fpm56
%{__install} -p -D -m 0755 %{SOURCE2} %{buildroot}/data/lemp/php-5.6.31/etc/php-fpm.conf
%{__install} -p -D -m 0755 %{SOURCE3} %{buildroot}/data/lemp/php-5.6.31/etc/php.ini
%{__install} -p -D -m 0755 %{SOURCE4} %{buildroot}/data/lemp/php-5.6.31/etc/php-fpm.d/www.conf
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

%clean
rm -rf %{buildroot} 

%files
%defattr (-,root,root,0755)
%{_prefix}
%attr(0755,root,root) /etc/rc.d/init.d/php-fpm56

%changelog
* Thu Sep 14 2017 xiaozhenkai.com <zhenkai_1123@qq.com> - 5.6.31-1
- Initial version

# End Of nginx.spec

