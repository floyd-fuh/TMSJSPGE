
# This script can be used to run the policy creator over an entire file collection (corpus) of
# input files the Java application parses. When it is finished you have all necessary permissions
# in the file all_policies.txt

# This script assumes that list_of_files.txt is a list of all corpus files with absolutes paths
# specified and that all of these paths include "input_directory". Or in other words input_directory
# is a parent direcotry of every file in the list.

touch all_policies.txt
touch policy.txt
while read p; do
    echo $p
    cat policy.txt all_policies.txt|grep -v input_directory|sort -u > tmp_policies.txt
    mv tmp_policies.txt all_policies.txt
    rm policy.txt
    ./create_java_security_policy.py policy.txt -cp subfolder/:exampleDependency.jar org.example.package.SampleClass $p
    sleep 0.2
done <list_of_files.txt