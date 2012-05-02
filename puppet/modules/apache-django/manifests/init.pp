class apache-django {
    include apache-django::install, apache-django::config, apache-django::service
#    include apache-common
}

class apache-django::install {
    package { "httpd":
        ensure => present,
    }
#    realize Package [ "httpd" ]
}

class apache-django::config {
    File {
        require => Class[ "apache-django::install" ],
        notify  => Class[ "apache-django::service" ],
    }

    file { "/etc/logrotate.d/httpd":
        ensure  => present,
        source  => "puppet:///modules/apache-django/etc/logrotate.d/httpd",
        require => Package["httpd"],
    }
}

class apache-django::service {
    service { "httpd":
        restart => "/usr/sbin/apachectl graceful",
        require => Class[ "apache-django::config" ],
        ensure  => running,
        enable  => true,
    }
#    realize Service [ "httpd" ]
}

