# The most sophisticated Java security policy generator EVAR (TMSJSPGE)
The Java Virtual Machine (JVM) has very powerful security features, such as the security manager
that allows writing policy files. The idea (how I use it) is to write a whitelist of files and network locations
(and other things) the Java process is allowed to access. If something is accessed that is not
on the whitelist, an Exception is thrown.

As already stated in 2004 ["there's currently no tool available to automatically generate a policy file for specific code"](http://www2.sys-con.com/itsg/virtualcd/java/archives/0501/neville/index.html).
So when you want a write a policy file for your code, you have to do it manually. Or maybe there
is a tool and I simply didn't find it (please enlighten me!). Anyway, it's a shame I had to hack such
an ugly ugly python-that-parses-Java-exceptions script and am too lazy to do it nicely in Java, but hey,
better than nothing and you kind of only need it at "compile time". Afterwards you have a policy file
and you can get rid of this tool again.

By floyd, https://floyd.ch, @floyd_ch, 2018

## How it works
Long story short, I wrote a horrible python script that launches Java processes to wait for an exception,
then add the permission stated in the exception to the policy and restart the process. It starts with an
empty policy file only allowing read/write/delete to temporary file locations and will launche the Java process
once per permission necessary. This is done until no more exceptions occure and the necessary policy file was 
created. Of course if your Java process is a daemon that doesn't exit when "all work is done", it might still
throw permission exceptions during runtime, but at least it starts cleanly with that policy file.

## Howto

Let's say you usually start your Java application with the following command line:

```java -cp subfolder/:exampleDependency.jar org.example.package.SampleClass input_file.txt```

The first thing you probably want to do, is manually add read access to "exampleDependency.jar" in the 
[create_java_security_policy.py](create_java_security_policy.py) script by uncommenting the example in the
`policies` variable and adjust the jar file name. Although this is not always necessary, you can end up with
a nullpointer exception when the code tries to access ressources (eg. xml oder json configuration files) inside
the jar file. Because that nullpointer exception does not state that it is a problem with the security manager/policy,
this tool can not add that policy permission by itself. And you might get confused as well, so please do this step now.

Then you will need to execute the [create_java_security_policy.py](create_java_security_policy.py) script
like this (where policy.txt does not exist yet):

```./create_java_security_policy.py policy.txt -cp subfolder/:exampleDependency.jar org.example.package.SampleClass input_file.txt```

The script will now fill policy.txt for you. It will start a subprocess with the following Java command line several times with different policy.txt files:

```java -Djava.security.manager -Djava.security.policy=policy.txt -Djava.io.tmpdir=/tmp/ -cp subfolder/:exampleDependency.jar org.example.package.SampleClass input_file.txt```

After it ran through, you can now run your Java application with security manager turned on with the same command line:

```java -Djava.security.manager -Djava.security.policy=policy.txt -Djava.io.tmpdir=/tmp/ -cp subfolder/:exampleDependency.jar org.example.package.SampleClass input_file.txt```

Of course you should now try all the functionalities of your application, to make sure it won't throw an exception and that it does not need any further permissions.
For example you should try all different parsers that could touch the `input_file.txt` of our example application and therefore run with a lot of different `input_file.txt`.

That's it, you have a nice policy.txt file now.

## Batch parsing corpus

You want to make sure that no permissions are missing for any of the input files and behavior of your Java program.
The file [quick_ndirty_batch_corpus.sh](quick_ndirty_batch_corpus.sh) is an example of how the [create_java_security_policy.py](create_java_security_policy.py)
script can be run over an entire folder of input files.