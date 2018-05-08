#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
import os

WHITELIST_POLICY_START = "grant {\n"
WHITELIST_POLICY_END = "};\n"

policies = [
    # IMPORTANT, recommendation:
    # Add a read permission for jar files you are starting and passing on the command line:
    # Otherwise if it is reading a ressource from inside the JAR file you might
    # get a NullPointerException and the security manager actually doesn't print
    # a nice message in that case. So for example if you have an exampleDependency.jar
    # which is located in the cwd, uncomment the following:
    # '    permission java.io.FilePermission "exampleDependency.jar", "read";\n',
    
    # Also important: if your application writes temporary files, use this:
    '    permission java.io.FilePermission "/tmp/*", "read, write, delete";\n'
]

def write_policy(policy_file, cmd_line):
    f = file(policy_file, "w")
    f.write(WHITELIST_POLICY_START+"".join(policies)+WHITELIST_POLICY_END)
    f.close()
    #print(cmd_line)
    process = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    #print(output)
    #print(err)
    # Parsing Java exceptions with Python is like parsing HTML with Regex
    if 'Exception in thread "main" ' in err:
        exception_line = None
        for line in err.split("\n"):
            if line.startswith('Exception in thread "main" '):
                exception_line = line
                break
        try:
            issue = exception_line.split('("')[1].split('")')[0].replace('"', '')
            issues_splitted = issue.split(" ")
            policies.append('    permission '+issues_splitted[0]+' "'+'", "'.join(issues_splitted[1:])+'";\n')
            write_policy(policy_file, cmd_line)
        except Exception, e:
            # Not the well-formed exception we can handle
            print(err)
    else:
        print(err)
        print(output)

def main():
    if len(sys.argv) <= 2:
        print("Usage:")
        print(sys.argv[0]+" <policy_filename> <arguments to java command line>")
        print("For example:")
        print(sys.argv[0]+" security_policy.txt -cp subfolder/:exampleDependency.jar org.example.package.SampleClass input_file.txt")
    else:
        policy_file = sys.argv[1]
        if os.path.exists(policy_file):
            print("The file "+policy_file+" already exists, please remove it and rerun this tool")
        else: 
            cmd_line = ["java", "-Djava.security.manager", "-Djava.security.policy="+policy_file, "-Djava.io.tmpdir=/tmp/"]
            cmd_line.extend(sys.argv[2:])
            print("Good, this is how we are going to start the Java process:")
            print(" ".join(cmd_line))
            write_policy(policy_file, cmd_line)

if __name__ == "__main__":
    main()
