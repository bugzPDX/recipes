#!/usr/bin/env python
import os
import sys
import os.path

#!/usr/bin/env python

# Cater for Virtual env, add to sys.path
pwd = os.path.abspath(os.path.dirname(__file__))
project = os.path.basename(pwd)
new_path = pwd.strip(project)
activate_this = os.path.join(new_path,'env','bin','activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipes_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
