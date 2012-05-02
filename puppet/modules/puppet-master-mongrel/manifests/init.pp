class puppet-master {
    include puppet-master::install, puppet-master::config, puppet-master::service
    include apache-proxy
}

class puppet-master::install {

    Package {
        ensure => installed,
    }

    package {[  
        "puppet-server",
        "rubygems", "rubygem-mongrel", "ruby-devel",
        "mysql", "mysql-devel", "mysql-server", "ruby-mysql",
        "libxml2", "libxml2-devel", "libxslt", "libxslt-devel",
        "make", "gcc", "sqlite-devel", "mod_ssl",
       ]: ensure => [ installed, present ] } 

    package { "fog": 
        ensure      => [ "1.1.2", "--no-rdoc", "-no-ri net-ssh" ], 
        provider    => gem,
        require     => Package [ "rubygems" ],
    }
    package { "sqlite3": 
        ensure      => [ "1.3.5", "--no-rdoc", "-no-ri net-ssh" ], 
        provider    => gem,
        require     => [ Package [ "rubygems" ], Package [ "sqlite-devel" ]]
    }
    package { "net-ssh": 
        ensure      => [ "2.1.4", "--no-rdoc", "-no-ri net-ssh" ], 
        provider    => gem,
        require     => Package [ "rubygems" ],
    }
    package { "activerecord": 
        ensure      => [ "3.0.10", "--no-rdoc", "-no-ri net-ssh" ], 
        provider    => gem,
        require     => Package [ "rubygems" ],
    }
#    package { "mysql-gem":
#        alias       => "mysql",
#        ensure      => [ "2.8.1", "--no-rdoc", "-no-ri net-ssh",
#                         "--with-mysql-config=/usr/bin/mysql_config" ],
#        provider    => gem,
#        require     => Package [ "rubygems" ],
#    }

    ## The above package resource causes a duplicate definition error,
    ## but we need both the gem and rpm installed - using an exec to
    ## ensure the gem

    exec { "install-mysql-gem":
        command     => "gem install mysql -v=2.8.1 -with-mysql-config=/usr/bin/mysql_config",
        unless      => "gem list | grep mysql | grep 2.8.1",
    }

    package { "git": }
    
    realize Package[ "httpd" ]
}

class puppet-master::config {

    $puppet_path = "/var/lib/puppet/Infrastructure/puppet/"

    File {
        require     => [ Class[ "puppet-master::install" ], Package[ "httpd" ] ],
        notify      => Class[ "puppet-master::service" ],
    }

    file { "/etc/sysconfig/puppetmaster":
        ensure      => present,
        source      => "puppet:///modules/puppet-master/etc/sysconfig/puppetmaster",
    }

### Use apache to balance requests to mongrel
    file { "/etc/httpd/conf.d/puppetmaster.conf":
        content     => template("puppet-master/etc/httpd/conf.d/puppetmaster.conf")
    }

### Custom apache config based on: http://projects.puppetlabs.com/projects/1/wiki/Using_Mongrel
    file { "/etc/httpd/conf/httpd.conf":
        source      => "puppet:///modules/puppet-master/etc/httpd/conf/httpd.conf",
        ensure      => present,
    }

### We need to tune the db for stored configs, based on suggestions here:
### http://www.masterzen.fr/2009/03/18/omg-storedconfigs-killed-my-database/
### as well as diagnostics found using percona toolkit: http://www.percona.com/software/percona-toolkit/
    file { "tune-mysql-storedconfigs":
        path        => "/etc/my.cnf",
        source      => "puppet:///modules/puppet-master/etc/my.cnf",
        ensure      => present,
        owner       => root,
        group       => root,
    }

### build key so that update script can pull from git
#    file { "/var/lib/puppet/.ssh":
#        ensure          => directory,
#        owner           => puppet,
#        group           => puppet,
#        mode            => 600,
#        source          => "puppet:///modules/puppet-master/var/lib/puppet/.ssh/",
#        sourceselect    => all,
#        recurse         => true,
#    }
    
### Make sure logging directory present
    file { "/var/log/puppet":
        ensure          => present,
        owner           => puppet,
        group           => puppet,
    }

    file { "/etc/httpd/conf.d/keepalive.conf":
        source          => "puppet:///modules/puppet-master/etc/httpd/conf.d/keepalive.conf",
    }

    file { "/etc/security/limits.d/99-puppet.conf":
        source          => "puppet:///files/security/limits.d/99-puppet.conf",
    }

### Ensure that the config parser check is present
    file { "puppet-parser-libs":
        path            => "/usr/lib/ruby/site_ruby/1.8/puppet",
        ensure          => directory,
        owner           => root,
        group           => root,
        mode            => 644,
        source          => "puppet:///modules/puppet-master/usr/lib/ruby/site_ruby/1.8/puppet",
        sourceselect    => all,
        recurse         => true,
    }

#### default database creation - for stored configs
#    exec { "mysql < $puppet_path/files/puppet.sql": 
#        unless          => "mysqlshow | grep puppet",
#        onlyif          => "test -f ",
#        require         => Package [ "mysql" ],
#    }

#    realize File[ "apache-proxy" ]
}

class puppet-master::service {

    service { "puppetmaster":
        enable      => true,
        pattern     => "/usr/sbin/puppetmasterd",
        ensure      => running,
        hasstatus   => true,
    }

}
