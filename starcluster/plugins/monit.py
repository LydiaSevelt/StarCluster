# Copyright 2019 Lydia Sevelt
#
# This file is part of StarCluster.
#
# StarCluster is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# StarCluster is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with StarCluster. If not, see <http://www.gnu.org/licenses/>.

import os

from starcluster import static
from starcluster.clustersetup import ClusterSetup

class MonitBalancers(ClusterSetup):
    """Plugin to integrate monit to run load balancers"""
    # This needs a lot of work
    def __init__(self):
        pass
    
    def run(self, nodes, master, user, user_shell, volumes):
        """Write file and reload monit"""
        self.cluster_name = master.cluster_groups[0].name.replace(static.SECURITY_GROUP_PREFIX, '')
        # write the monit config file to the default path
        path = "/home/ec2-user/.starcluster/monit.d/" + self.cluster_name + "_lb"
        f = open(path, 'w')
        try:
            f.write(
                "check process " + self.cluster_name + "_lb with pidfile /home/ec2-user/.starcluster/loadbalancers/" + self.cluster_name + "_lb.pid\n"
                "\tstart program = \"/bin/bash -l -c 'eval $(/home/ec2-user/saml2aws script); /usr/local/bin/starcluster loadbalance -n 1 -m 10 -w 60 -i 10 -k 2 -q " + self.cluster_name + " > /home/ec2-user/.starcluster/loadbalancers/" + self.cluster_name + "_lb.log & echo $! > /home/ec2-user/.starcluster/loadbalancers/" + self.cluster_name + "_lb.pid'\"\n"
                "\tstop program  = \"/bin/bash -l -c 'kill -9 $(cat /home/ec2-user/.starcluster/loadbalancers/" + self.cluster_name + "_lb.pid)'\"\n")
        finally:
            f.close()
        os.system("monit -c /home/ec2-user/.starcluster/monit.conf reload")
    
    def on_shutdown(self, nodes, master, user, user_shell, volumes):
        """Stop service in monit and remove file"""
        self.cluster_name = master.cluster_groups[0].name.replace(static.SECURITY_GROUP_PREFIX, '')
        os.system("monit -c /home/ec2-user/.starcluster/monit.conf stop " + self.cluster_name + "_lb")
        os.unlink("/home/ec2-user/.starcluster/monit.d/" + self.cluster_name + "_lb")
