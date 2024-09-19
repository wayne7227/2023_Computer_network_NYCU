from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink


def runIperf(net, src, dst, bw_limit, duration=10):
   src_node = net.get(src)
   dst_node = net.get(dst)


   # Display information about the client connection, TCP port, and TCP window size
   print("Starting iperf session from {} to {} with bandwidth limit {} Mbps".format(
       src, dst, bw_limit))
   #print("Client {}: Connecting to Server {} on TCP port {}".format(
   #    src_node.name, dst_node.name, 5001))
   #print("TCP Window Size: 16 MB")  # Assuming a fixed window size for simplicity


   # Start the iperf server on the destination host
   iperf_server_cmd = 'iperf -s -t {} &'.format(duration)
   server_process = dst_node.popen(iperf_server_cmd)


   # Construct and execute the iperf client command on the source host
   iperf_client_cmd = 'iperf -c {} -t {} -b {}M'.format(dst_node.IP(), duration, bw_limit)
   client_process = src_node.popen(iperf_client_cmd)


   client_exit_code = client_process.wait()


   # Terminate iperf processes on the server and client if needed
   #dst_node.cmd('pkill -f "{}"'.format(iperf_server_cmd))
   #src_node.cmd('pkill -f "{}"'.format(iperf_client_cmd))


   # Print the iperf client output
   #print("iperf client output:")
   print(client_process.stdout.read().decode('utf-8'))


   # Check if the bandwidth exceeded the set value
   if client_exit_code == 0:
       client_output = client_process.communicate()[0].decode('utf-8')
       if "Mbits/sec" in client_output:
           measured_bandwidth = float(client_output.split()[-2])
           if measured_bandwidth > bw_limit:
               print("Warning: Bandwidth exceeded the set limit. Terminating iperf processes.")


   print("iperf session completed")


def createTopo():
   net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)


   # Add Ryu controller
   c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)


   # Add switches
   s1 = net.addSwitch('s1')
   s2 = net.addSwitch('s2')
   s3 = net.addSwitch('s3')
   s4 = net.addSwitch('s4')
   s5 = net.addSwitch('s5')
   s6 = net.addSwitch('s6')


   # Add hosts
   h1 = net.addHost('h1')
   h2 = net.addHost('h2')
   h3 = net.addHost('h3')
   h4 = net.addHost('h4')
   h5 = net.addHost('h5')
   h6 = net.addHost('h6')
   h7 = net.addHost('h7')
   h8 = net.addHost('h8')
   h9 = net.addHost('h9')


   # Add links
   net.addLink(h1, s1)
   net.addLink(h2, s1)
   net.addLink(s1, s2)
   net.addLink(s2, h3)
   net.addLink(s2, s3)
   net.addLink(s3, h4)
   net.addLink(s3, h5)
   net.addLink(s1, s4)
   net.addLink(s4, h6)
   net.addLink(s4, s5)
   net.addLink(s5, h7)
   net.addLink(s5, s6)
   net.addLink(s6, h8)
   net.addLink(s6, h9)


   print("Starting network")
   net.build()
   c1.start()
   s1.start([c1])
   s2.start([c1])
   s3.start([c1])
   s4.start([c1])
   s5.start([c1])
   s6.start([c1])


   # Set IP addresses for hosts
   for i in range(1, 10):
       net.get('h{}'.format(i)).cmd('ifconfig h{}-eth0 10.0.0.{} netmask 255.255.255.0'.format(i, i))


   # Set up iperf sessions
   runIperf(net, 'h1', 'h2', 5)
   runIperf(net, 'h1', 'h3', 10)
   runIperf(net, 'h4', 'h5', 15)
   runIperf(net, 'h6', 'h8', 20)


   print("Running CLI")
   CLI(net)


   print("Stopping network")
   net.stop()


if _name_ == '_main_':

   setLogLevel('info')
   createTopo()