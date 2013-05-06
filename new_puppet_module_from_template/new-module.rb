#!/usr/bin/ruby

require 'erb'
require 'fileutils'
require 'pp'

module_name = ARGV[0]

dirnames = [ "templates", "manifests", "files" ]

dirnames.each { |dir|
  FileUtils.mkdir_p(File.join(Dir.pwd, module_name, dir))
}

template = "
class <%= module_name %>::install {

    # Defaults for all packages:
    Package {
        ensure => installed
    }

    # Specific packages:

}

class <%= module_name %>::service {

    # Defaults for all services:
    Service {
        require => Class[\"<%= module_name %>::config\"],
        ensure  => running,
        enable  => true
    }

    # Specific services:

}

class <%= module_name %>::config {

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

class <%= module_name %> {

    include <%= module_name %>::install, <%= module_name %>::config, <%= module_name %>::service

}
"

renderer = ERB.new(template)
File.open(File.join(Dir.pwd, module_name, "manifests", "init.pp"),'w' ) { |f|
  f.write(renderer.result())
}

puts "created new manifest set #{module_name}"
