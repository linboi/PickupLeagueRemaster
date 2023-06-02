import subprocess


class rasp:

    def restart_pi():
        # restart pi
        process = subprocess.Popen(
            ["sudo", "reboot"], shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print(output)

    def update_pi():
        # update bot version
        process = subprocess.Popen(
            ["git", "pull", "origin", "release"], shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print(output)
        return output
