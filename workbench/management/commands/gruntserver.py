"""
Integrate Grunt into Django with `manage.py gruntserver`

This is meant to replace `manage.py runserver` for Grunt-powered
projects.
"""
import atexit
import os
import signal
import subprocess

from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver


class Command(runserver.Command):
    """
    Create the gruntserver command to replace runserver
    """
    _grunt_processes = []

    def _start_grunt_processes(self):
        """
        Start `grunt watch` for each project in `settings.XBLOCK_DIRECTORY`
        """
        self._write('>>> Start grunt')
        for directory in os.listdir(settings.XBLOCK_DIRECTORY):
            path_absolute_directory = os.path.join(
                settings.XBLOCK_DIRECTORY,
                directory,
            )
            path_absolute_file = os.path.join(
                path_absolute_directory,
                'Gruntfile.js',
            )
            if os.path.isfile(path_absolute_file):
                process = subprocess.Popen(
                    [
                        'grunt watch --gruntfile={0}/Gruntfile.js --base={0}'.format(
                            path_absolute_directory,
                        )
                    ],
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=self.stdout,
                    stderr=self.stderr,
                )
                self._grunt_processes.append(process)
                self._write(
                    '>>> Fork grunt process, pid={0}: {1}'.format(
                        unicode(process.pid),
                        directory,
                    )
                )
                atexit.register(self._kill_grunt_process, process.pid)

    def _kill_grunt_process(self, pid):
        """
        Kill the specified Grunt process
        """
        self._write('>>> Kill grunt process, pid={0}'.format(
            unicode(pid),
        ))
        os.kill(pid, signal.SIGTERM)

    def _write(self, value):
        """
        Write as unicode to STDOUT, appending a newline
        """
        self.stdout.write(unicode(value))
        self.stdout.write(u'\n')

    def inner_run(self, *args, **kwargs):
        """
        Handle launching of child processes
        """
        self._start_grunt_processes()
        return super(Command, self).inner_run(*args, **kwargs)
