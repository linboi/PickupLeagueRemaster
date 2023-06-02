import subprocess


class rasp:

    def restart_pi():
        # restart pi
        process = subprocess.Popen(
            ["sudo", "reboot"], stdout=subprocess.PIPE)

    def update_pi():
        # update bot version
        process = subprocess.Popen(
            ["git", "pull", "origin", "release"], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        return output
