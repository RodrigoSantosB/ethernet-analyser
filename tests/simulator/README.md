### FOR TO SIMULATION VIRTUAL ETHERNET CONECTION

`sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth0 up
sudo ip link set veth1 up
ip link show
`

```bash
sudo python sender.py /caminho/para/seu/arquivo.pcapng veth0
sudo python receiver.py veth1
```