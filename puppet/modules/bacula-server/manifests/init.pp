class bacula-server {
    include bacula-server::reqs, bacula-server::install, bacula-server::config, bacula-server::services
}

class bacula-server::reqs {
    package { "mysql-server": ensure => present }
#    package { "bacula": ensure => present }
}

class bacula-server::install {
    Package {
        require => Class[ "bacula-server::reqs" ],
    }
    package { "bacula": ensure => present }
}

class bacula-server::config {
    File {
        require => Class[ "bacula-server::install" ],
        notify  => Class[ "bacula-server::services" ],
    }

    file { "/etc/bacula/bacula-dir.conf":
        source => "puppet:///bacula-server/bacula-dir.conf",
    }

    file { "/etc/bacula/bacula-sd.conf":
        source => "puppet:///bacula-server/bacula-sd.conf",
    }

    file { "/etc/bacula/bacula-fd.conf":
        source => "puppet:///bacula-server/bacula-fd.conf",
    }
}

class bacula-server::services {
    service { "bacula-director":
        name    => "bacula-director",
        ensure  => running,
        enable  => true,
        require => Class[ "bacula-server::config" ],
    }
    service { "bacula-sd":
        name    => "bacula-sd",
        ensure  => running,
        enable  => true,
        require => Class[ "bacula-server::config" ],
    }
    service { "bacula-fd":
        name    => "bacula-fd",
        ensure  => running,
        enable  => true,
        require => Class[ "bacula-server::config" ],
    }
}
