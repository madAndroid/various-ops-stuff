class python-vpackages {
    include python-vpackages::install
    include python-vpackages::updates
}

class python-vpackages::install {

    @package { 'mod_wsgi':              ensure => installed }
    @package { 'libjpeg':               ensure => installed }
    @package { 'MySQL-python':          ensure => installed }
    @package { 'protobuf':              ensure => installed }
    @package { 'protobuf-compiler':     ensure => installed }
    @package { 'protobuf-python':       ensure => installed }
    @package { 'python-imaging':        ensure => installed }
    @package { 'python-pip':            ensure => installed }
    @package { 'python-setuptools':     ensure => installed }
    @package { 'python-devel':          ensure => installed }
    @package { 'python-boto':           ensure => installed }
#    @package { 'gcc':                   ensure => installed }
#    @package { 'make':                   ensure => installed }

}

class python-vpackages::updates {
    
    @exec { "update-pip":
        command     => 'pip-python install -U pip',
        onlyif      => 'rpm -qa | grep python-pip-0.8',
        unless      => '/usr/bin/which pip && pip --version | awk \'{ print $2 }\' | cut -d. -f1 | grep 1',
        require     => Package [ "python-pip" ],
    }

}
