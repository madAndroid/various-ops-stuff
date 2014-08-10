#!/usr/bin/ruby

require 'erb'
require 'fileutils'
require 'pp'

module_path = ARGV[0]
module_name = File.basename(ARGV[0])

dirnames = [ "templates", "manifests", "features", "files" ]

dirnames.each { |dir|
  FileUtils.mkdir_p(File.join(Dir.pwd, module_path, dir))
}

template = <<-'EOF'
# Copyright 2012-2013 The Scale Factory Limited. All rights reserved.

class <%= module_name %> {

#
# Commonly used hiera variables read in here, for convenience
#

}
EOF

renderer = ERB.new(template)
File.open(File.join(Dir.pwd, module_path, "manifests", "init.pp"),'w' ) { |f|
  f.write(renderer.result())
}

puts "created new manifest set #{module_name} in #{File.join(Dir.pwd, module_path)}"
