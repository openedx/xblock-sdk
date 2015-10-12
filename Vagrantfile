# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure('2') do |config|
  config.vm.box = 'ubuntu/precise64'
  config.vm.synced_folder '.', '/home/vagrant'
  config.vm.network 'forwarded_port', guest: 8008, host: 8008
  config.vm.provision 'shell' do |shell|
    shell.path = 'Makefile'
    shell.args = [
      'provision',
    ]
  end
  config.vm.provider 'virtualbox' do |vb|
    # We need to increase this to install lxml
    vb.memory = 1024
  end
end
