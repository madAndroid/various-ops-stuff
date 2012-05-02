class apache-common {
    include apache-common::install, apache-common::config, apache-common::service
}

class apache-common::install {
    @package { "httpd":         ensure => installed }
}

class apache-common::config {
#    File {
#        require => Package[ "apache2" ],
#    }
#
#    @file { "/etc/apache2/mods-enabled/proxy_balancer.load":
#        ensure => "/etc/apache2/mods-available/proxy_balancer.load",
#    }
#
#    @file { "/etc/apache2/mods-enabled/proxy_http.load":
#        ensure => "/etc/apache2/mods-available/proxy_http.load",
#    }
#
#    @file { "/etc/apache2/mods-enabled/proxy.load":
#        ensure => "/etc/apache2/mods-available/proxy.load",
#    }
#
#    @file { "/etc/apache2/mods-enabled/proxy.conf":
#        ensure => "/etc/apache2/mods-available/proxy.conf",
#    }
}

class apache-common::service {
    @service { "httpd":  
        restart => "/usr/sbin/apachectl graceful",
        require => Class[ "apache-common::install" ],
        ensure  => running,
        enable  => true,
    }
}
