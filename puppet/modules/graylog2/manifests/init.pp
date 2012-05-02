class graylog2 {
    include graylog2::install, graylog2::config, graylog2::service
}

class graylog2::install {
    include graylog2::install::server
    include graylog2::install::web_interface
}

class graylog2::install::server {
    package { "graylog2-server"
        ensure      => "0.9.6",
    }
}

class graylog2::install::web_interface {

    $gl2_wroot  = "/opt/graylog2-web-interface"
    $rbenv_root = "$gl2_wroot/rbenv"
    $rbenv_ver  = "$rbenv_root/.rbenv-version"
    $ruby_ver   = "1.9.2-p318"

    Exec    {   
        path        => [
            '/usr/local/bin',
            '/usr/bin', 
            '/usr/sbin', 
            '/bin',
            '/sbin',
            "$rbenv_root/shims",
            "$rbenv_root/bin",
            ],
        logoutput   => true,
        cwd         => $gl2_wroot,
    }

    package { "graylog2-web-interface":
        ensure      => "0.9.6",
    }

    exec { "$name-set-rbenv":
        command     => "rbenv local $ruby_ver",
        unless      => "rbenv local | grep $ruby_ver | grep $rbenv_ver",
        notify      => "$name-rbenv-rehash",
    }

    exec { "$name-rbenv-rehash":
        command     => "rbenv rehash",
        refreshonly => true,
    }

    exec { "$name-gembundle":
        command     => "rbenv which bundle && bundle install",
        timeout     => "900",
        onlyif      => Exec [ "$name-set-rbenv" ],
        unless      => "test -f $gl2_wroot/Gemfile.lock",
        notify      => [ Exec [ "$name-passenger-compile" ],
                         Exec [ "$name-rbenv-rehash" ]],
    }

    exec { "$name-passenger-compile":
        command     => "rbenv which passenger; rbenv rehash; passenger package-runtime",
        user        => graylog2,
        unless      => "test -f .passenger",
    }

}

class graylog2::config {
    include graylog2::config::server
    include graylog2::config::web_interface
}

class graylog2::config::server {

    File {
        require     => Class[ "graylog2::install::server" ],
        notify      => Class[ "graylog2::service::server" ],
    }

    file { "/etc/sysconfig/graylog2-server":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/sysconfig/graylog2-server",
    }

    file { "/etc/graylog2.conf":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/graylog2.conf",
    }

    file { "/etc/init.d/graylog2-web":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/sysconfig/puppetmaster",
    }

}

class graylog2::config::web_interface {

    File {
        require     => Class[ "graylog2::install::web_interface" ],
        notify      => Class[ "graylog2::service::web_interface" ],
    }

    file { "/etc/sysconfig/graylog2-web":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/sysconfig/puppetmaster",
    }

    file { "/etc/init.d/graylog2-web":
        ensure      => present,
        source      => "puppet:///modules/graylog2/etc/sysconfig/puppetmaster",
    }

}

class graylog2::service::server {

    Service {
        require     => Class [ "graylog2::config::server" ],
    }

    service { "graylog2-server":
        enable      => true,
        pattern     => "/usr/sbin/puppetmasterd",
        ensure      => running,
        hasstatus   => true,
    }

}

class graylog2::service::web_interface {

    Service {
        require     => Class [ "graylog2::config::web_interface" ],
    }

    service { "graylog2-web":
        enable      => true,
        pattern     => "/usr/sbin/puppetmasterd",
        ensure      => running,
        hasstatus   => true,
    }

}

