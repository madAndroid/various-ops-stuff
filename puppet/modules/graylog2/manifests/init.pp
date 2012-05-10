class graylog2 {
    include graylog2::server 
    include graylog2::web_interface
}

class graylog2::server {
    include graylog2::server::install, graylog2::server::config, graylog2::server::service
    include graylog2::common
}

class graylog2::web_interface {
    include graylog2::web_interface::install, graylog2::web_interface::config, graylog2::web_interface::service
    include graylog2::common
}

class graylog2::common {
    include user_accounts::graylog2
}

class graylog2::server::install {
    package { "graylog2":
        ensure      => installed,
    }
}

class graylog2::web_interface::install {

    $gl2web_base    = "/opt/graylog2-web-interface"

    include apache-passenger

    realize Package [ "httpd" ]
    realize Package [["httpd-devel"],["zlib-devel"],["openssl-devel"],["make"],["gcc"],["gcc-c++"],["libcurl-devel"]]
    realize Package [ "passenger" ]
    realize Exec [ "passenger-install-apache2-module" ]

    Exec    {   
        logoutput   => true,
        cwd         => $gl2web_base,
    }

    package { "graylog2-web-interface":
        ensure      => installed,
    }

    package { "bundler":
        ensure      => "1.0.21",
        provider    => gem,
        require     => Package ["graylog2-web-interface"],
    }

    exec { "bundle-install-graylog2-web":
        command     => "bundle install",
        require     => Package [ "bundler" ],
        onlyif      => "test -f $gl2web_base/Gemfile",
        unless      => "test -f $gl2web_base/Gemfile.lock",
    }

}

class graylog2::server::config {

    File {
        require     => Class[ "graylog2::server::install" ],
        notify      => Class[ "graylog2::server::service" ],
        owner       => graylog2,
        group       => adm,
        mode        => 664,
    }

    $gl2srv_base    = "/opt/graylog2-server"

    file {[ "$gl2srv_base",
            "$gl2srv_base/conf",
            "$gl2srv_base/log",
            "$gl2srv_base/run",
        ]:
        ensure      => directory,
        require     => Package [ "graylog2" ],
    }

    file { "/opt/graylog2-server/conf/graylog2.conf":
        ensure      => present,
        source      => "puppet:///modules/graylog2/opt/graylog2-server/conf/graylog2.conf",
    }

    file { "/etc/init.d/graylog2-server":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/init.d/graylog2-server",
        owner       => root,
        group       => root,
        mode        => 755,
    }

### this has been moved to logging_server class:
#    file { "/etc/sysconfig/graylog2-server":
#        ensure      => present,
#        source      => "puppet:///modules/graylog2/etc/sysconfig/graylog2-server",
#        mode        => 644,
#    }

### Server logs - java process is very noisy when logging enabled
    file { "/etc/logrotate.d/graylog2-server":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/logrotate.d/graylog2-server",
        mode        => 644,
    }

}

class graylog2::web_interface::config {

    File {
        require     => Class[ "graylog2::web_interface::install" ],
        notify      => Class[ "graylog2::web_interface::service" ],
    }

    $gl2web_base    = "/opt/graylog2-web-interface"

    file { "$gl2web_base":
        ensure      => directory,
        owner       => graylog2,
        group       => adm,
        require     => Package [ "graylog2-web-interface" ],
    }

    file { "/etc/httpd/conf.d/graylog2-web.conf":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/httpd/conf.d/graylog2-web.conf",
    }

    file { "/opt/graylog2-web-interface/config/mongoid.yml":
        ensure      => present,
        source      => "puppet:///modules/graylog2/opt/graylog2-web-interface/config/mongoid.yml",
    }
}

class graylog2::server::service {
    service { "graylog2-server":
        enable      => true,
        ensure      => running,
        hasrestart  => true,
        require     => File [ "/etc/init.d/graylog2-server" ],
    }
}

class graylog2::web_interface::service {
    realize Service [ "httpd" ]
}
