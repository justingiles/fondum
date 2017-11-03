import subprocess


def cmdline(command):
    ''' run a command from the local OS and capture the output a list of strings '''
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        shell=True
    )
    raw_text = process.communicate()[0].decode("utf-8") 
    return raw_text.split("\n")

# eof
