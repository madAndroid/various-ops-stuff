#!/usr/bin/ruby

require 'erb'
require 'fileutils'
require 'pp'

module_path = ARGV[0]
module_name = File.basename(ARGV[0])

dirnames = [ "templates", "manifests", "files" ]

dirnames.each { |dir|
  FileUtils.mkdir_p(File.join(Dir.pwd, module_path, dir))
}

template = "
class <%= module_name %>::params {


}

class <%= module_name %>::install (

    ) inherits <%= module_name %>::params {

    # Defaults for all packages:
    Package {
        ensure => installed
    }

    # Specific packages:

}

class <%= module_name %>::service (

    ) inherits <%= module_name %>::params {

    # Defaults for all services:
    Service {
        require => Class[\"<%= module_name %>::config\"],
        ensure  => running,
        enable  => true
    }

    # Specific services:

}

class <%= module_name %>::config (

    ) inherits <%= module_name %>::params {

    # Defaults for all files in here:
    File { 
        require => Class[\"<%= module_name %>::install\"],
        notify  => Class[\"<%= module_name %>::service\"],
        owner   => root,
        group   => root,
        mode    => 644
    }

    # Specific files
    # (use content => template(\"<%= module_name %>/<path>\") to use templates from
    #  this module).

}

#
# Class: <%= module_name %>
#
# Description of <%= module_name %>
#

class <%= module_name %> (

    ) inherits <%= module_name %>::params {

    include <%= module_name %>::install

    class <%= module_name %>::config {

    }

    include <%= module_name %>::service

}
"

renderer = ERB.new(template)
File.open(File.join(Dir.pwd, module_path, "manifests", "init.pp"),'w' ) { |f|
  f.write(renderer.result())
}

puts "created new manifest set #{module_name}"
