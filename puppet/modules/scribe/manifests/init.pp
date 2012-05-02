class scribe::client {
    include scribe::common
    include scribe::config::client
}

class scribe::master {
    include scribe::common
    include scribe::config::master
}

class scribe::common {
    include scribe::install, scribe::config, scribe::service
}

class scribe::install {

    include v-packages
    Package {
        ensure => installed,
    }
    package {[ "scribe", "scribe-python" ]:
        ensure => "2.2-2.amzn1",
    }
    realize Package [ "thrift", "thrift-python",
                      "thrift-cpp", "thrift-cpp-devel" ]
    realize Package [ "fb303", "fb303-devel", "fb303-python"]
}

class scribe::config {

    File {
        require     => Class[ "scribe::install" ],
        notify      => Class[ "scribe::service" ],
        owner       => root,
        group       => root,
    }

    file { "/etc/init.d/scribed":
        source      => "puppet:///modules/scribe/etc/init.d/scribed",
        mode        => 755,
    }
}

class scribe::config::client {

    $loghost = "log_master"
    $port    = $port

    File {
        require     => Class[ "scribe::install" ],
        notify      => Class[ "scribe::service" ],
        mode        => 644,
        owner       => root,
        group       => root,
    }

    file { "/etc/sysconfig/scribed":
        content     => template("scribe/etc/sysconfig/scribed.erb")
    }

    file { "/etc/scribed/graylog2.conf":
        content     => template("scribe/etc/scribed/client.conf.erb")
    }
}

class scribe::config::master {

    File {
        require     => Class[ "scribe::install" ],
        notify      => Class[ "scribe::service" ],
        mode        => 644,
        owner       => root,
        group       => root,
    }

    file { "/etc/sysconfig/scribed":
        content     => template("scribe/etc/sysconfig/scribed.erb")
    }

    file { "/etc/scribed/master.conf":
        content     => template("scribe/etc/scribed/master.conf.erb")
    }
}

class scribe::service {
    service { "scribed":
        enable      => true,
        ensure      => running,
        restart     => "/etc/init.d/scribed restart",
        require     => File [ "/etc/init.d/scribed" ],
    }
}
