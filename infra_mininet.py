#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import threading
import time

def thread_oscilacao(net):
    """
    Roda em segundo plano alterando o Traffic Control (tc) do kernel do Linux 
    para simular oscilações reais de banda (Ex: congestionamento ou sinal ruim).
    """
    h1 = net.get('h1')
    intf = h1.defaultIntf() # Pega a placa de rede de saída do Servidor
    
    time.sleep(5) # Aguarda os nós iniciarem os testes
    
    try:
        while True:
            # Fase 1: Rede Ótima (10 Mbps) - DASH deve subir para HIGH
            info('\n[!] OSCILAÇÃO: Subindo banda para 10 Mbps...\n')
            intf.config(bw=10)
            time.sleep(15)
            
            # Fase 2: Rede Ruim (2 Mbps) - DASH deve cair para LOW
            info('\n[!] OSCILAÇÃO: Derrubando banda para 2 Mbps...\n')
            intf.config(bw=2)
            time.sleep(15)
    except:
        pass # Ignora erros quando a rede for desligada no 'exit'

def montar_topologia():
    setLogLevel('info')
    net = Mininet(controller=Controller, switch=OVSKernelSwitch, link=TCLink)

    info('*** Adicionando Controlador\n')
    net.addController('c0')

    info('*** Adicionando Hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    info('*** Adicionando Switch\n')
    s1 = net.addSwitch('s1')

    info('*** Criando Links Base\n')
    # O h1->s1 começará com 10 Mbps, mas a thread vai alterar isso dinamicamente
    net.addLink(h1, s1, bw=10, delay='20ms', max_queue_size=100, use_htb=True)
    net.addLink(h2, s1, bw=10, delay='20ms', max_queue_size=100, use_htb=True)

    info('*** Iniciando a Rede\n')
    net.start()

    # ---- INICIA A MAGIA DA OSCILAÇÃO AQUI ----
    t_osc = threading.Thread(target=thread_oscilacao, args=(net,), daemon=True)
    t_osc.start()

    info('*** CLI do Mininet aberta\n')
    CLI(net)

    info('*** Encerrando a Rede\n')
    net.stop()

if __name__ == '__main__':
    montar_topologia()