import os
# Various config options are set in this file. Details for the options,
# is included just before the option.

# configuration options for wtf-forms:
WTF_CSRF_ENABLED = True
SECRET_KEY = 'PLfqHmAoVbJpfinR8EV3'

# Configuration for landing page:
PRELAUNCH = True

# File upload settigns:
UPLOAD_FOLDER = "drtysnow/data/resort_images"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg' 'gif', 'png'])
