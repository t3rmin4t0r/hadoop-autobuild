
JDK_URL=http://download.oracle.com/otn-pub/java/jdk/6u38-b05/jdk-6u38-linux-x64.bin
JDK_BIN=$(shell basename $(JDK_URL))

$(JDK_BIN): 
	wget -c --no-cookies --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com" $(JDK_URL) 

jdk: $(JDK_BIN)
	yes | bash -x ./$(JDK_BIN)
	mv jdk.1.6.0_38 /usr/lib/jvm/jdk 
	echo "export JAVA_HOME=/usr/lib/jvm/jdk-1.6/"> /etc/profile.d/java.sh 

epel:
	rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
	yum makecache

git: epel
	yum -y install git-core gcc gcc-g++ pdsh 

maven: jdk
	wget http://apache.techartifact.com/mirror/maven/maven-3/3.0.4/binaries/apache-maven-3.0.4-bin.tar.gz
	mkdir /opt/hadoop-build/
	tar -C /opt/hadoop-build/ --strip-components=1 -xzvf ~/apache-maven-3.0.4-bin.tar.gz

protobuf: git 
	wget -c http://protobuf.googlecode.com/files/protobuf-2.4.1.tar.bz2
	tar -xvf protobuf-2.4.1.tar.bz2
	cd protobuf-2.4.1; \
	./configure --prefix=/opt/hadoop-build/; \
	make -j4; \
	make install

hadoop: git maven protobuf
	git clone git://git.apache.org/hadoop-common.git hadoop 
	export PATH=$$PATH:/opt/hadoop-build/bin/; \
	cd hadoop/; git branch branch-2 --track origin/branch-2; \
	git checkout branch-2; \
	mvn package -Pdist -DskipTests;

install: hadoop
	rsync -avP hadoop/hadoop-dist/target/hadoop-2*/ /opt/hadoop/
	cp gen-conf.py /opt/hadoop/etc/hadoop/
	cd /opt/hadoop/etc/hadoop/; python gen-conf.py
