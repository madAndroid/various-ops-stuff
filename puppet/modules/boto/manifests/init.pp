class boto {
    include boto::install, boto::config, boto::service
    include python-vpackages
}

class boto::install {

    Package {   ensure  => installed }
    Exec    {   require => Package [ "python-pip" ]}

    realize Package [[ "python-setuptools" ],
                    [ "python-pip" ],
                    [ "python-devel" ]]

    realize Exec [ "update-pip" ]

    # install boto via pip
    exec { "install-boto":
        command     => 'pip install \'boto==2.2.2\'',
        unless      => 'pip freeze | grep boto | grep 2.2.2',
        require     => Exec [ "update-pip" ], 
    }
    
}

class boto::config {

    File {
        require => Class[ "boto::install" ],
        notify  => Class[ "boto::service" ],
    }

}

class boto::service {

}
