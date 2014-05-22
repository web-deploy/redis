%define GitStamp 21027786
Summary: redis-sentinel
Name: redis-sentinel
Version: 2.8.9.%{GitStamp}
Release: 1tagged2
License: BSD
Group: Applications/Multimedia
URL: http://code.google.com/p/redis/

Source0: %{name}-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: gcc, make
Requires(post): /sbin/chkconfig /usr/sbin/useradd
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
Provides: redis-sentinel

Packager: jdi

%description
Redis is a key-value database. It is similar to memcached but the dataset is
not volatile, and values can be strings, exactly like in memcached, but also
lists and sets with atomic operations to push/pop elements.

In order to be very fast but at the same time persistent the whole dataset is
taken in memory and from time to time and/or when a number of changes to the
dataset are performed it is written asynchronously on disk. You may lose the
last few queries that is acceptable in many applications but it is as fast
as an in memory DB (beta 6 of Redis includes initial support for master-slave
replication in order to solve this problem by redundancy).

Compression and other interesting features are a work in progress. Redis is
written in ANSI C and works in most POSIX systems like Linux, *BSD, Mac OS X,
and so on. Redis is free software released under the very liberal BSD license.


%prep
%setup

%build
%{__make} 32bit

%install
%{__rm} -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
%{__install} -Dp -m 0755 src/redis-sentinel %{buildroot}%{_sbindir}/redis-sentinel-tagged
%{__install} -Dp -m 0755 utils/redis-sentinel.sysv %{buildroot}%{_sysconfdir}/init.d/redis-sentinel
%{__install} -p -d -m 0755 %{buildroot}%{_localstatedir}/log/redis
%{__install} -p -d -m 0755 %{buildroot}%{_localstatedir}/run/redis

%pre
/usr/sbin/useradd -c 'redis' -u 515 -s /sbin/nologin -r -d /home/redis redis 2> /dev/null || :

%preun
if [ $1 = 0 ]; then
    # make sure redis service is not running before uninstalling

    # when the preun section is run, we've got stdin attached.  If we
    # call stop() in the redis init script, it will pass stdin along to
    # the redis-cli script; this will cause redis-cli to read an extraneous
    # argument, and the redis-cli shutdown will fail due to the wrong number
    # of arguments.  So we do this little bit of magic to reconnect stdin
    # to the terminal
    term="/dev/$(ps -p$$ --no-heading | awk '{print $2}')"
    exec < $term

    /sbin/service redis-sentinel stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del redis-sentinel
fi

%post
/sbin/chkconfig --add redis-sentinel

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%{_sbindir}/redis-sentinel-tagged
%{_sysconfdir}/init.d/redis-sentinel
%dir %attr(0755,redis,redis) %{_localstatedir}/log/redis
%dir %attr(0755,redis,redis) %{_localstatedir}/run/redis

%changelog
* Mon May 19 2014 - jdi at tagged dot com 21027786
- upped to trunk 21027786, May 8 2014
- sentinel-only spec file and sysv script

