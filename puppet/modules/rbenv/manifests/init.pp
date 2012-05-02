class rbenv {
    include rbenv::install, rbenv::config
}

class rbenv::params {

}

class rbenv::common {

    Exec    {   
        path => [
            '/usr/local/bin',
            '/usr/bin', 
            '/usr/sbin', 
            '/bin',
            '/sbin',
            "$rbenv_root/shims",
            "$rbenv_root/bin",
            "$rbenv_bin",
            ],
        logoutput => true,
    }
 
    exec { "rbenv-rehash":
        command     => "rbenv rehash"
    }

}

class rbenv::install::base {

    $rbenv_root = "/opt/rbenv"

    Package {   ensure  => installed }
   
    package { "rbenv":
        ensure      => "0.3.0",
    }

}

class rbenv::install::ruby_rpm ($rbenv_rpm = "rbenv-ruby", $ruby_version = "1.9.2"){

    Package {   ensure  => installed }

    package { "$rbenv_rpm":
        ensure      => "$ruby_version",
    }

}

class rbenv::install::ruby ($ruby_revision = "1.9.2-p318"){

    include rbenv::common
    include rbenv::install::base

    $rbenv_root = "/opt/rbenv"
    $rbenv_bin  = "$rbenv_root/versions/$ruby_version/bin/"
    $rbenv_ver  = "$rbenv_root/.rbenv-version"

    Exec    {   
        require => Package [ "rbenv" ],
        path => [
            '/usr/local/bin',
            '/usr/bin', 
            '/usr/sbin', 
            '/bin',
            '/sbin',
            "$rbenv_root/shims",
            "$rbenv_root/bin",
            "$rbenv_bin",
            ],
        logoutput => true,
    }
    
    # install ruby 1.9.2 via rbenv 
    exec { "install-rbenv-$ruby_revision":
        command     => "rbenv install $ruby_revision",
        unless      => "rbenv versions | grep $ruby_revision",
        notify      => Exec [ "rbenv-rehash" ],
        require     => Package [ "rbenv" ],
    }

    # install ruby 1.9.2 via rbenv 
    exec { "set-rbenv-$ruby_revision":
        command     => "rbenv local $ruby_revision",
        cwd         => "$rbenv_root"
        unless      => "rbenv local | grep $ruby_revision | grep $rbenv_ver",
        notify      => Exec [ "rbenv-rehash" ],
        require     => Package [ "rbenv" ],
    }

}

class rbenv::config {

    File {
        require => Class[ "rbenv::install" ],
        notify  => Class[ "rbenv::service" ],
    }

}
