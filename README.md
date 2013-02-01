hadoop-autobuild
================

This is a hacky way of getting a hadoop cluster quickly up on EC2.

First up, spin up nodes and pick one as a master.

Checkout this code on the master and create a file named "slaves" filled with the other hostnames (or for a single node cluster, you can say "localhost" in it).

run "make install" to download & compile hadoop/branch-2

then "make start" to start the daemons on all the nodes correctly.

You can edit gen-conf.py to add more config options and play around with the configs.

There are 3 assumptions made on this 

1) all nodes are identical
2) you have root everywhere
3) root is passphraseless (or at least, agent handled)
