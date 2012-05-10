class scribe::client {
    include scribe::common
    include scribe::config::client
}

class scribe::master {
    include scribe::common
    include scribe::config::master
}

class scribe::common {
    
    $scribe_storage_dir = "/opt/scribe"
    $buffer_path        = "/opt/scribe/buffer"
    $log_path           = "/opt/scribe/log"

    include scribe::install, scribe::config, scribe::service

    file { [ "$buffer_path",
             "$log_path", 
        ]:
        ensure  => directory,
        owner   => scribe,
        group   => adm,
        mode    => 755,
        require => File [ "$scribe_storage_dir" ],
    }

    file { "/etc/logrotate.d/scribed":
        ensure  => present,
        source  => "puppet:///modules/scribe/etc/logrotate.d/scribed",
        owner   => root,
        group   => root,
    }

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
    
    include user_accounts::scribe

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

    $buffer_path       = "$scribe_buffer_dir"
    $log_path          = "$scribe_log_dir"
    $scribe_role       = "client"

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

    file { "/etc/scribed/client.conf":
        content     => template("scribe/etc/scribed/client.conf.erb")
    }
}

class scribe::config::master {

    $storage_path   = "$scribe_storage_dir"
    $buffer_path    = "$scribe_buffer_dir"
    $log_path       = "$scribe_log_dir"
    $scribe_role    = "master"

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
    
    file { [ "/opt/scribe/storage",
             "/opt/scribe/buffer/graylog2",
        ]:
        ensure      => directory,
        owner       => scribe,
        group       => adm,
        mode        => 755,
    }

}

class scribe::service {
    service { "scribed":
        ensure      => running,
        enable      => true,
        provider    => "redhat",
        restart     => "/etc/init.d/scribed restart",
        require     => File [ "/etc/init.d/scribed" ],
        notify      => Service [ "logstash" ],
    }
}
