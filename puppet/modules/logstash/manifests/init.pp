class logstash::client {
    include logstash::install, logstash::config, logstash::service
}

class logstash::install {
    package { "logstash":
        ensure      => "1.1.0_scribe-2.amzn1",
    }
}

class logstash::config {

    $base_dir = "/opt/logstash"

    include user_accounts::logstash

    File {
        require     => Class[ "logstash::install" ],
        notify      => Class[ "logstash::service" ],
        owner       => logstash,
        group       => adm,
    }

    file {[ "/etc/logstash",
            "/var/run/logstash",
            "$base_dir",
            "$base_dir/log",
            "$base_dir/lib",
            "$base_dir/run",
            "$base_dir/rbenv",
        ]:
        ensure      => directory,
    }

    file { "$base_dir/log/logstash.log":
        mode        => 664,
    }

    file { "/etc/sysconfig/logstash":
        ensure      => present,
        source      => "puppet:///modules/logstash/etc/sysconfig/logstash",
    }

    file { "/etc/logstash/logstash.conf":
        ensure      => present,
        source      => "puppet:///modules/logstash/etc/logstash/logstash.conf",
    }

    file { "/etc/init.d/logstash":
        ensure      => present,
        source      => "puppet:///modules/logstash/etc/init.d/logstash",
        owner       => root,
        group       => root,
        mode        => 755,
    }
}

class logstash::service {
    service { "logstash":
        ensure      => running,
        enable      => true,
        provider    => "redhat",
        pattern     => "/opt/logstash/lib/logstash/runner.rb",
        restart     => "/etc/init.d/logstash restart",
        require     => File [ "/etc/init.d/logstash" ],
    }
}
