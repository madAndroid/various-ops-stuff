class django_server {

    include django_server::install
    include django_server::config
    include django_server::service

    include apache-django
    include memcached_host

}

class django_server::install {

    include python-vpackages::install

    Package {
        ensure      => installed,
        require     => Class ["Apache-django"], 
    }

    File {
        ensure      => present,
        owner       => root,
        group       => root,
        require     => Class ["Apache-django"], 
    }

    file { '/etc/yum.repos.d/rpmforge.repo':
        mode        => 444,
        source      => "puppet:///files/django_server/etc/yum.repos.d/rpmforge.repo",
        require     => [ File ['/etc/yum.repos.d'], Exec['fetch-gpg-rpmforge' ] ],
    }

    exec { "fetch-gpg-rpmforge":
        command     => "rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt",
        unless      => "rpm -qa gpg-* | grep gpg-pubkey-6b8d79e6-3f49313d",
    }

    package{ "python-django":
        require     => File ["/etc/yum.repos.d/rpmforge.repo"]
    }
 
    realize Package [[ "mod_wsgi" ],
                    [ "libjpeg" ],
                    [ "MySQL-python" ],
                    [ "protobuf" ],
                    [ "protobuf-compiler" ],
                    [ "protobuf-python" ], 
                    [ "python-imaging" ]]

}

class django_server::config {

    include django_server::common

    $deploy_user = 'deploy-www'

### Defaults for config files:

    File {
        ensure      => present,
        owner       => root,
        group       => root,
        require     => Class[ "django_server::install" ],
        notify      => Service [ "httpd" ]
    }

    file { "/tmp/$deploy_user-django_signup_upload":
        ensure      => directory,
        owner       => $deploy_user,
        group       => $deploy_user,
        mode        => 700,
    }

    file { "/var/log/mahifx/django.log":
        owner       => $deploy_user,
        group       => $deploy_user,
        mode        => 664,
    }

    # Update FAQs from SalesForce
    case $vpc_dns_root {
        prod: {
            cron { "django_manage_update_faq":
                command     => "python /var/django/mahi/src/project/manage.py update_faq > /home/$deploy_user/manage.py-update_faq.log",
                user        => $deploy_user,
                minute    => 0,
                hour      => fqdn_rand(24)
            }
        }
        default: {
            cron { "django_manage_update_faq":
                command     => "python /var/django/mahi/src/project/manage.py update_faq > /home/$deploy_user/manage.py-update_faq.log",
                user        => $deploy_user,
                minute      => fqdn_rand(60),
                ensure      => absent
            }
        }
    }

    # Cleanup old sessions
    cron { "django_manage_cleanup":
        command     => "python /var/django/mahi/src/project/manage.py cleanup > /home/$deploy_user/manage.py-cleanup.log",
        user        => $deploy_user,
        minute    => fqdn_rand(60)
    }

### Apache config:

	file { "/etc/httpd/conf":
	    ensure  => directory,
	    recurse => true,
	    mode    => 444,
        source  => "puppet:///files/django_server/etc/httpd/conf/",
	    purge   => true,
	    force   => true
	}

    file { "/etc/httpd/conf/httpd.conf":
        content => template("django_server/etc/httpd/conf/httpd.conf.erb")
    }

	file { "/etc/httpd/conf.d":
	    ensure  => directory,
	    recurse => true,
	    mode    => 444,
        source  => "puppet:///files/django_server/etc/httpd/conf.d/",
	    purge   => true,
	    force   => true
	}

    file { "/etc/httpd/conf.d/mahi.conf":
        ensure       => present,
        content      => template("django_server/etc/httpd/conf.d/mahi.conf.erb")
    }

### Realize virtualized resource:
    realize File [ "/etc/mahifx/conf.d/local_settings.py"]

### Hive has a password for access
    case $vpc_dns_root {
        hive: {
            file { "/etc/httpd/conf/htpasswd":
                source      => "puppet:///files/django_server/etc/httpd/conf/htpasswd"
            }
        }
        prod: { }
    }

}

class django_server::common {

    $deploy_user = 'deploy-www'

    File { 
        owner       => $deploy_user,
        group       => $deploy_user,
    }

### Virtualize common resources
    @file { [ "/var/django",
             "/etc/mahifx",
             "/etc/mahifx/conf.d",
             "/var/log/mahifx",
        ]:
        ensure      => directory,
        mode        => 775,
    }

    @file { "/etc/mahifx/conf.d/local_settings.py":
        mode        => 775,
        content     => template("django_server/etc/mahifx/conf.d/local_settings.py.erb")
    }

    @file { "/etc/mahifx/fabfile.py":
        mode        => 775,
        source      => "puppet:///files/www_ci_server/etc/mahifx/fabfile.py",
    }

}

class django_server::service {

}
