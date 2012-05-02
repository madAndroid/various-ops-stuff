class apache-proxy {
    include apache-proxy::install, apache-proxy::config, apache-proxy::service
    include apache-common
}

class apache-proxy::install {
    realize Package[ "httpd" ]
}

class apache-proxy::config {
    File {
        require => Package[ "httpd" ],
    }

    @file { "apache-proxy":
        path    => "/etc/httpd/conf/httpd.conf",
        ensure  => present,
        source  => "puppet:///modules/apache-proxy/etc/httpd/conf/httpd.conf",
    }
    
#    @file { "/etc/apache2/mods-enabled/proxy_balancer.load":
#        ensure => "/etc/apache2/mods-available/proxy_balancer.load",
#    }
#    @file { "/etc/apache2/mods-enabled/proxy_http.load":
#        ensure => "/etc/apache2/mods-available/proxy_http.load",
#    }
#    @file { "/etc/apache2/mods-enabled/proxy.load":
#        ensure => "/etc/apache2/mods-available/proxy.load",
#    }
#    @file { "/etc/apache2/mods-enabled/proxy.conf":
#        ensure => "/etc/apache2/mods-available/proxy.conf",
#    }

}

class apache-proxy::service {
    realize Service [ "httpd" ]
}
