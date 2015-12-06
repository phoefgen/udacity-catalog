from drtysnow import drtysnow

# Note: this turns on remote access to the site. This is to enable the dev env
# to be built inside a container, and accessed from the hypervisor. 
drtysnow.debug = True
drtysnow.run(host='0.0.0.0')
