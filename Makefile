VERSION=branch-2.3
PROTOC_VERSION=2.5.0
JDK_BASE_DIR=/usr/lib/jvm/jdk7/
JDK_VERSION=jdk1.7.0_51
INSTALL_ROOT=/grid/0/opt/

ARCH=$(shell uname -p)
YUM=$(shell which yum)
APT=$(shell which apt-get)
PDSH=pdsh -R ssh
DFS=$(shell ls /grid/*/tmp/dfs/name/current/ 2>/dev/null | head -n 1) 

ifeq ($(ARCH), x86_64)
        JDK_URL=http://download.oracle.com/otn-pub/java/jdk/7u51-b13/jdk-7u51-linux-x64.tar.gz
        JDK_BIN=$(shell basename $(JDK_URL))
else
        JDK_URL=http://download.oracle.com/otn-pub/java/jdk/7u51-b13/jdk-7u51-linux-i586.tar.gz
        JDK_BIN=$(shell basename $(JDK_URL))
endif

$(JDK_BIN):
	wget --no-check-certificate -O $(JDK_BIN) -c --no-cookies --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com" $(JDK_URL)
	echo "export JAVA_HOME=/usr/lib/jvm/jdk7/"> /etc/profile.d/java.sh
	ln -s /usr/lib/jvm/jdk7/ /usr/lib/jvm-exports/jdk7

jdk: $(JDK_BIN)
	mkdir -p /usr/lib/jvm/
	test -d $(JDK_BASE_DIR) || (tar -zxf $(JDK_BIN) && mv $(JDK_VERSION) $(JDK_BASE_DIR))
	echo "export JAVA_HOME=$(JDK_BASE_DIR)"> /etc/profile.d/java.sh
	mkdir -p /usr/lib/jvm-exports/jdk7

epel:
ifneq ($(YUM),)
	test -f /etc/yum.repos.d/epel.repo || rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
	yum makecache
endif

git: epel
ifneq ($(YUM),)
	yum -y install git-core 
	yum -y install gcc gcc-c++ 
	yum -y install pdsh
	yum -y install cmake
	yum -y install zlib-devel openssl-devel 
endif
ifneq ($(APT),)
	apt-get install -y git gcc g++ python man cmake zlib1g-dev libssl-dev pdsh
endif

maven: jdk
	wget -c http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
	-- mkdir /opt/hadoop-build/
	tar -C /opt/hadoop-build/ --strip-components=1 -xzvf apache-maven-3.0.5-bin.tar.gz

ant: jdk
	wget -c http://psg.mtu.edu/pub/apache//ant/binaries/apache-ant-1.9.0-bin.tar.gz 
	-- mkdir /opt/ant/
	tar -C /opt/ant/ --strip-components=1 -xzvf apache-ant-1.9.0-bin.tar.gz
	-- yum -y remove ant

protobuf: git 
	wget -c http://protobuf.googlecode.com/files/protobuf-$(PROTOC_VERSION).tar.bz2
	tar -xvf protobuf-$(PROTOC_VERSION).tar.bz2
	test -f /opt/hadoop-build/bin/protoc || \
	(/opt/hadoop-build/ export PATH=$$PATH:/usr/bin/; cd protobuf-$(PROTOC_VERSION); \
	./configure --prefix=/opt/hadoop-build/; \
	make -j4; \
	make install)

hadoop: git maven protobuf
	test -d hadoop || git clone git://git.apache.org/hadoop-common.git hadoop 
	-- cd hadoop; git pull --rebase
	export PATH=$$PATH:/opt/hadoop-build/bin/; \
	cd hadoop/; git branch $(VERSION) --track origin/$(VERSION); \
	git checkout $(VERSION); \
	. /etc/profile; \
	mvn package -Pnative -Pdist -DskipTests -Dmaven.javadoc.skip=true;


hadoop/hadoop-dist/target/: 
	make hadoop

install: hadoop/hadoop-dist/target/
	rsync -avP hadoop/hadoop-dist/target/hadoop-2*/ $(INSTALL_ROOT)/hadoop/
	cp slaves gen-conf.py $(INSTALL_ROOT)/hadoop/etc/hadoop/
	cd $(INSTALL_ROOT)/hadoop/etc/hadoop/; python gen-conf.py

/opt/hadoop: install

/root/.ssh/id_rsa: 
	ssh-keygen -f /root/.ssh/id_rsa -N ''
	echo "StrictHostKeyChecking=no" >> ~/.ssh/config

propogate: /opt/hadoop slaves /root/.ssh/id_rsa
	cp slaves $(INSTALL_ROOT)/hadoop/etc/hadoop/;
	ssh-copy-id localhost;
	for host in $$(cat slaves | grep -v localhost) ; do \
		rsync -avP ~/.ssh/ ~/.ssh/; \
		rsync --exclude=\*.out --exclude=\*.log -avP $(INSTALL_ROOT)/ $$host:$(INSTALL_ROOT); \
		rsync -avP $(JDK_BASE_DIR) $$host:$(JDK_BASE_DIR)/; \
		scp /etc/profile.d/java.sh $$host:/etc/profile.d/java.sh; \
	done

#start: propogate
start: 
	test ! -z $(DFS) || $(INSTALL_ROOT)/hadoop/bin/hdfs namenode -format
	$(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh start namenode
	$(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh start resourcemanager
	$(INSTALL_ROOT)/hadoop/sbin/mr-jobhistory-daemon.sh start historyserver
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh start datanode && $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh start nodemanager'

stop:
	$(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh stop namenode
	$(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh stop resourcemanager
	$(INSTALL_ROOT)/hadoop/sbin/mr-jobhistory-daemon.sh stop historyserver
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh stop datanode && $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh stop nodemanager'
	

rm-restart:
	$(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh stop resourcemanager
	$(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh start resourcemanager

nm-restart:
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh stop nodemanager'
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh start nodemanager'

restart-slaves:
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh stop datanode && $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh stop nodemanager'
	$(PDSH) -w $$(tr \\n , < slaves) 'source /etc/profile; $(INSTALL_ROOT)/hadoop/sbin/hadoop-daemon.sh start datanode && $(INSTALL_ROOT)/hadoop/sbin/yarn-daemon.sh start nodemanager'
