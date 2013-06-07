import socket
hostname = socket.getfqdn()
from glob import glob

namenode = hostname
resourcemanager = hostname
total_megs=8192

volumes = glob("/grid/[0-9]*/")

def distribute(path):
	return ",".join(["%s/%s" % (v,path) for v in volumes])

core = """
<configuration>

<property>
  <name>mapreduce.clientfactory.class.name</name>
  <value>org.apache.hadoop.mapred.YarnClientFactory</value>
</property>

 <property>
    <name>yarn.server.principal</name>
    <value>nm/localhost@LOCALHOST</value>
  </property>

<property>
  <name>fs.default.name</name>
  <value>hdfs://%(namenode)s:56565</value>
  <!--
  <value>file:///</value>
  -->
  <description>The name of the default file system.  A URI whose
  scheme and authority determine the FileSystem implementation.  The
  uri's scheme determines the config property (fs.SCHEME.impl) naming
  the FileSystem implementation class.  The uri's authority is used to
  determine the host, port, etc. for a filesystem.</description>
</property>

<property>
  <name>hadoop.tmp.dir</name>
  <value>%(hadoop_tmp)s</value>
  <description>A base for other temporary directories.</description>
</property>
<property>
	<name>dfs.namenode.name.dir</name>
	<value>%(hadoop_name)s</value>
</property>

  <property>
    <name>hadoop.security.authentication</name>
    <!--
    <value>kerberos</value>
    -->
    <value>simple</value>
  </property>

<!--
  <property>
    <name>hadoop.security.authorization</name>
    <value>true</value>
  </property>
-->

 <property>
   <name>hadoop.cluster.administrators</name>
   <value>*</value>
 </property>

<!--
  <property>
    <name>hadoop.security.auth_to_local</name>
    <value>
      DEFAULT
    </value>
  </property>
-->

  <property>
    <name>hadoop.security.auth_to_local</name>
    <value>RULE:[1:$1@$0](.*@localhost)s/@.*//
DEFAULT
</value>
  </property>


  <property>
    <name>dfs.namenode.kerberos.principal</name>
    <!--
    <value>hdfs/localhost@LOCALHOST</value>
    -->
    <value>hdfs/localhost@localhost</value>
  </property>
  <property>
    <name>dfs.datanode.kerberos.principal</name>
    <value>hdfs/localhost@localhost</value>
  </property>
  <property>
    <name>dfs.namenode.keytab.file</name>
    <value>/etc/krb5.keytab</value>
  </property>
  <property>
    <name>dfs.datanode.keytab.file</name>
    <value>/etc/krb5.keytab</value>
  </property> 
  <property>
    <name>dfs.namenode.delegation.key.update-interval</name>
    <value>604800000</value>
  </property>
  <property>
    <name>dfs.namenode.delegation.token.renew-interval</name>
    <value>604800000</value>
  </property>
  <property>
    <name>dfs.namenode.delegation.token.max-lifetime</name>
    <value>604800000</value>
  </property>

  <property>
    <name>dfs.permissions</name>
    <value>true</value>
  </property>

  <property>
    <name>dfs.namenode.kerberos.https.principal</name>
    <value>hdfs/localhost@localhost</value>
  </property>

</configuration>
""" % {'namenode':namenode, 'hadoop_name':distribute('dfs/name'), 'hadoop_tmp':distribute('tmp')}

hdfs = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<!-- Put site-specific property overrides in this file. -->

<configuration>

<property>
  <name>dfs.client.read.shortcircuit</name>
  <value>true</value>
</property>

<property>
  <name>dfs.block.local-path-access.user</name>
  <value>root</value>
</property>

<property>
  <name>hadoop.tmp.dir</name>
  <value>%(hadoop_tmp)s</value>
  <description>A base for other temporary directories.</description>
</property>

<property>
  <name>dfs.http.address</name>
  <value>%(namenode)s:50070</value>
  <description>
    The address and the base port where the dfs namenode web ui will listen on.
    If the port is 0 then the server will start on a free port.
  </description>
</property>

<property>
  <name>dfs.https.port</name>
  <value>0</value>
  <description>
    The address and the base port where the dfs namenode web ui will listen on.
    If the port is 0 then the server will start on a free port.
  </description>
</property>

<property>
  <name>dfs.datanode.failed.volumes.tolerated</name>
  <value>0</value>
  <description>The number of volumes that are allowed to
  fail before a datanode stops offering service. By default
  any volume failure will cause a datanode to shutdown.
  </description>
</property>

<property>
<name>dfs.datanode.data.dir</name>
<value>%(hadoop_data)s</value>
</property>

<property>
  <name>dfs.datanode.address</name>
  <value>0.0.0.0:50010</value>
  <description>
    The address where the datanode server will listen to.
    If the port is 0 then the server will start on a free port.
  </description>
</property>

<property>
  <name>dfs.datanode.http.address</name>
  <value>0.0.0.0:50011</value>
  <description>
    The datanode http server address and port.
    If the port is 0 then the server will start on a free port.
  </description>
</property>

<property>
  <name>dfs.block.access.token.enable</name>
  <value>false</value>
  <final>true</final>
</property>

<property>
  <name>dfs.domain.socket.path</name>
	<value>/var/run/hdfs.sock</value>
</property>


</configuration>
""" % {'namenode' : namenode, 'hadoop_tmp' : distribute('tmp'), 'hadoop_data' : distribute('dfs/data')}

yarn = """<?xml version="1.0"?>
<configuration>

 <property>
    <name>yarn.resourcemanager.principal</name>
    <value>rm/localhost@localhost.eglbp.corp.yahoo.com</value>
  </property>


 <property>
    <name>yarn.resourcemanager.admin.acl</name>
    <value>false</value>
  </property>

 <property>
    <name>yarn.resourcemanager.am.max-retries</name>
    <value>4</value>
  </property>


 <property>
    <name>yarn.nodemanager.principal</name>
    <value>nm/localhost@localhost.eglbp.corp.yahoo.com</value>
  </property>

  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce.shuffle</value>
  </property>

  <property>
    <name>yarn.nodemanager.aux-services.shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>

  <property>
    <name>mapreduce.jobhistory.keytab</name>
    <value>/etc/krb5.keytab</value>
  </property>

  <property>
    <name>mapreduce.jobhistory.principal</name>
    <value>rm/localhost@localhost.eglbp.corp.yahoo.com</value>
  </property>


<!-- All resourcemanager related configuration properties -->
  <property>
    <name>yarn.resourcemanager.address</name>
    <value>%(resourcemanager)s:8032</value>
  </property>

  <property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>%(resourcemanager)s:8031</value>
  </property>

  <property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>%(resourcemanager)s:8030</value>
  </property>

  <property>
    <name>yarn.resourcemanager.nodes.exclude-path</name>
    <value>/opt/hadoop/etc/hadoop/excluded-nodes</value>
  </property>


<!--
  <property>
     <name>yarn.resourcemanager.webapp.address</name>
     <value>localhost:8088</value>
  </property>
-->

<!--
  <property>
    <name>yarn.resourcemanager.scheduler.class</name>
    <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler</value>
  </property>
-->
 
  <property>
    <name>yarn.server.resourcemanager.application.expiry.interval</name>
    <value>60000</value>
  </property>

  <property>
    <name>yarn.server.resourcemanager.keytab</name>
    <value>/etc/krb5.keytab</value>
  </property>

<!-- All nodemanager related configuration properties -->

  <property>
    <name>yarn.nodemanager.local-dirs</name>
    <value>%(hadoop_nm_local)s</value>
  </property>

  <property>
    <name>yarn.nodemanager.log-dirs</name>
    <value>%(hadoop_nm_log)s</value>
  </property>

  <property>
    <name>yarn.server.nodemanager.remote-app-log-dir</name>
   <!--
   <value>/tmp/test-logs</value>
   -->
   <value>/app-logs</value>
  </property>

  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
  </property>

  <property>
    <name>yarn.server.nodemanager.keytab</name>
    <value>/etc/krb5.keytab</value>
  </property>

  <property>
    <name>yarn.nodemanager.container-executor.class</name>
    <value>org.apache.hadoop.yarn.server.nodemanager.DefaultContainerExecutor</value>
    <!--
    <value>org.apache.hadoop.yarn.server.nodemanager.LinuxContainerExecutor</value>
    -->
  </property>

  <property>
    <name>yarn.server.nodemanager.address</name>
    <value>0.0.0.0:45454</value>
  </property>

  <!--<property>
    <name>yarn.nodemanager.health-checker.script.path</name>
    <value>/Users/vinodkv/tmp/conf/healthCheckerNotExisting</value>
    <description>Location of the node's health-check script on the local
    file-system.
    </description>
  </property>-->

  <property>
    <name>yarn.nodemanager.health-checker.interval-ms</name>
    <value>5000</value>
    <description>Frequency of the health-check run by the NodeManager
    </description>
  </property>

  <property>
    <name>yarn.server.nodemanager.healthchecker.script.timeout</name>
    <value>120000</value>
    <description>Timeout for the health-check run by the NodeManager
    </description>
  </property>

  <property>
    <name>yarn.server.nodemanager.healthchecker.script.args</name>
    <value></value>
    <description>Arguments to be passed to the health-check script run
    by the NodeManager</description>
  </property>

  <property>
    <name>yarn.server.nodemanager.containers-monitor.monitoring-interval</name>
    <value>3000</value>
  </property>

  <property>
    <name>yarn.server.nodemanager.containers-monitor.resourcecalculatorplugin</name>
    <value>org.apache.hadoop.yarn.util.LinuxResourceCalculatorPlugin</value>
    <final>true</final>
  </property>

   <property>
     <name>yarn.server.nodemanager.reserved-physical-memory.mb</name>
     <value>-1</value>
   </property>

<!-- All MRAppManager related configuration properties -->

  <property>
    <name>yarn.server.mapreduce-appmanager.attempt-listener.bindAddress</name>
    <value>0.0.0.0</value>
  </property>

  <property>
    <name>yarn.server.mapreduce-appmanager.client-service.bindAddress</name>
    <value>0.0.0.0</value>
  </property>

  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>12288</value>
  </property>

  <property>
    <name>yarn.nodemanager.vmem-pmem-ratio</name>
    <value>20.0</value>
  </property>


  <property>
   <name>mapreduce.job.hdfs-servers</name>
   <value>${fs.default.name}</value>
 </property>

 <property>
   <name>yarn.server.nodemanager.jobhistory</name>
    <!-- cluster variant -->
    <value>/tmp/yarn/done</value>
    <description>The name of the default file system.  Either the
  literal string "local" or a host:port for NDFS.</description>
    <final>true</final>
  </property>

<property>
	<name>yarn.nodemanager.process-kill-wait.ms</name>
	<value>3600000</value>
</property>

<property>
	<name>yarn.nodemanager.sleep-delay-before-sigkill.ms</name>
	<value>3600000</value>
</property>

<property>
	<name>yarn.nodemanager.resource.memory-mb</name>
	<value>%(total_megs)d</value>
</property>

</configuration>
""" % {'resourcemanager' : resourcemanager, 'hadoop_tmp':distribute('tmp'), 'hadoop_nm_local':distribute('tmp/nm-local'), 'hadoop_nm_log':distribute('tmp/nm-logs'), 'total_megs': total_megs}

mapred = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<!-- Put site-specific property overrides in this file. -->

<configuration>

  <property>
    <name>mapreduce.shuffle.port</name>
    <value>8081</value>
  </property>


<property>
  <name>mapreduce.jobhistory.address</name>
  <value>%(jhs)s:10020</value>
</property>

<property>
    <name>yarn.app.mapreduce.am.staging-dir</name>
    <value>/tmp/${user.name}/.staging</value>
   </property>

   <property>
    <name>mapreduce.jobhistory.intermediate-done-dir</name>
    <value>/job-history-root/history/done_intermediate</value>
   </property>

   <property>
    <name>mapreduce.jobhistory.done-dir</name>
    <value>/job-history-root/history/done</value>
   </property>


<property>
  <name>mapred.job.tracker.history.completed.location</name>
  <value>/history/done/</value>
  <description> The completed job history files are stored at this single well 
  known location. If nothing is specified, the files are stored at 
  ${hadoop.job.history.location}/done.
  </description>
</property>

  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>


<property>
  <name>mapred.job.tracker</name>
  <value>localhost:55555</value>
  <description>The host and port that the MapReduce job tracker runs
  at.  If "local", then jobs are run in-process as a single map
  and reduce task.
  </description>
</property>


  <property>
    <name>mapreduce.jobtracker.kerberos.principal</name>
    <value>mapred/localhost@localhost.eglbp.corp.yahoo.com</value>
  </property>

  <property>
    <name>mapreduce.tasktracker.kerberos.principal</name>
    <value>mapred/localhost@localhost.eglbp.corp.yahoo.com</value>
  </property>

  <property>
    <name>mapreduce.jobtracker.keytab.file</name>
    <value>/etc/krb5.keytab</value>
  </property>

  <property>
    <name>mapreduce.tasktracker.keytab.file</name>
    <value>/etc/krb5.keytab</value>
  </property>

<property>
<name>mapreduce.history.server.http.address</name>
<value>%(jhs)s:63678</value>
</property>

<property>
<name>mapreduce.history.server.embedded</name>
<value>false</value>
<value>localhost:65678</value>
</property>

<property>
<name>mapreduce.history.server.embedded</name>
<value>false</value>
</property>

<property>
  <name>webinterface.private.actions</name>
  <value>true</value>
  <description> If set to true, the web interfaces of JT and NN may contain 
                actions, such as kill job, delete file, etc., that should 
                not be exposed to public. Enable this option if the interfaces 
                are only reachable by those who have the right authorization.
  </description>
</property>


<property>
  <name>mapred.jobtracker.taskScheduler</name>
 <value>org.apache.hadoop.mapred.JobQueueTaskScheduler</value>
  <description>The class responsible for scheduling the tasks.</description>
</property>

<property>
  <name>mapred.task.tracker.task-controller</name>
  <value>org.apache.hadoop.mapred.LinuxTaskController</value>
  <description>TaskController which is used to launch and manage task execution 
  </description>
</property>

<property>
  <name>mapred.jobtracker.completeuserjobs.maximum</name>
  <value>1</value>
  <description>The maximum number of complete jobs per user to keep around 
  before delegating them to the job history.</description>
</property>

<property>
<name>mapred.local.dir</name>
<value>/tmp/mapred-local/0_0,/tmp/mapred-local/0_1,/tmp/mapred-local/0_2,/tmp/mapred-local/0_3</value>
</property>
<property>
  <name>mapred.job.reuse.jvm.num.tasks</name>
  <value>-1</value>
  <description>How many tasks to run per jvm. If set to -1, there is
  no limit. 
  </description>
</property>

<property>
  <name>mapred.task.tracker.report.address</name>
  <value>127.0.0.1:0</value>
  <description>The interface and port that task tracker server listens on. 
  Since it is only connected to by the tasks, it uses the local interface.
  EXPERT ONLY. Should only be changed if your host does not have the loopback 
  interface.</description>
</property>

<property>
  <name>mapred.task.tracker.http.address</name>
  <value>0.0.0.0:0</value>
  <description>
    The task tracker http server address and port.
    If the port is 0 then the server will start on a free port.
  </description>
</property>

<property>
  <name>mapred.tasktracker.map.tasks.maximum</name>
  <value>2</value>
  <description>The maximum number of map tasks that will be run
  simultaneously by a task tracker.
  </description>
</property>

<property>
  <name>mapred.tasktracker.reduce.tasks.maximum</name>
  <value>2</value>
  <description>The maximum number of reduce tasks that will be run
  simultaneously by a task tracker.
  </description>
</property>

<!--
<property>
<name>mapred.cluster.map.memory.mb</name>
<value>1024</value>
</property>

<property>
<name>mapred.cluster.reduce.memory.mb</name>
<value>2048</value>
</property>


<property>
<name>mapred.job.map.memory.mb</name>
<value>1024</value>
</property>

<property>
<name>mapred.job.reduce.memory.mb</name>
<value>2048</value>
</property>


<property>
<name>mapred.cluster.max.map.memory.mb</name>
<value>2048</value>
</property>

<property>
<name>mapred.cluster.max.reduce.memory.mb</name>
<value>4096</value>
</property>
-->
<property>
<name>mapreduce.cluster.map.userlog.retain-size</name>
<value>1024</value>
</property>

<property>
<name>mapreduce.cluster.reduce.userlog.retain-size</name>
<value>1024</value>
</property>

<property>
  <name>mapred.tasktracker.taskmemorymanager.monitoring-interval</name>
  <value>1000</value>
  <description>The interval, in milliseconds, for which the tasktracker waits
   between two cycles of monitoring its tasks' memory usage. Used only if
   tasks' memory management is enabled via mapred.tasktracker.tasks.maxmemory.
   </description>
</property>

<property>
<name>mapred.map.task.debug.script</name>
<value></value>
<final>true</final>
</property>

<property>
  <name>mapred.job.queue.name</name>
  <value>default</value>
</property>

<property>
  <name>mapred.child.java.opts</name>
  <value>-Xmx1024m<!--yourkit:-agentpath:/opt/yourkit/bin/linux-x86-64/libyjpagent.so=dir=/grid/0/yjp,filters=/dev/null,tracing,disablej2ee--></value> 
</property>

<property>
  <name>mapreduce.job.counters.limit</name>
  <value>1024</value>
</property>

</configuration>
""" % ({'jhs':hostname})

open("core-site.xml", "w").write(core)
open("hdfs-site.xml", "w").write(hdfs)
open("yarn-site.xml", "w").write(yarn)
open("mapred-site.xml", "w").write(mapred)
