class fabric {
    include fabric::install, fabric::config, fabric::service
    include python-vpackages
}

class fabric::install {

    Package {   ensure  => installed }
    Exec    {   require => Package [ "python-pip" ]}

    realize Package [[ "python-setuptools" ],
                    [ "python-pip" ],
                    [ "python-devel" ]]

    realize Exec [ "update-pip" ]

    # install fabric via pip
    exec { "install-fabric":
        command     => 'pip install \'fabric==1.3.4\'',
        unless      => 'pip freeze | grep Fabric | grep 1.3.4',
        require     => Exec [ "update-pip" ], 
    }

}

class fabric::config {

    File {
        require => Class[ "fabric::install" ],
        notify  => Class[ "fabric::service" ],
    }

}

class fabric::service {

}
