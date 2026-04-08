import argparse
import socket

def main():
    # =====================================================================
    # BLOCO 1: RECEBIMENTO DE PARÂMETROS
    # Permite que a porta seja dinamicamente injetada pela topologia (Mininet)
    # =====================================================================
    parser = argparse.ArgumentParser(description="Smart Sampa: DASH Server")
    parser.add_argument('--port', type=int, default=8080, help="Porta TCP do servidor")
    args = parser.parse_args()

    HOST = '0.0.0.0' # Ouve em todas as interfaces de rede disponíveis
    PORT = args.port
    
    # =====================================================================
    # BLOCO 2: DEFINIÇÃO DO PERFIL DE MÍDIA (VÍDEO VIRTUAL)
    # Define o peso exato dos blocos de vídeo (Chunks) para emular o tráfego
    # - HIGH: 1 Megabyte por segundo de vídeo (Alta Resolução)
    # - LOW: 250 Kilobytes por segundo de vídeo (Baixa Resolução)
    # =====================================================================
    CHUNK_HIGH_SIZE = 1024 * 1024
    CHUNK_LOW_SIZE = 250 * 1024

    # =====================================================================
    # BLOCO 3: INICIALIZAÇÃO DO SOCKET TCP
    # Configura o servidor no paradigma "Pull" (espera o cliente pedir)
    # =====================================================================
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # SO_REUSEADDR evita o erro "Address already in use" ao reiniciar testes rápidos
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[*] Servidor DASH (Sequenciado) aguardando conexões na porta TCP {PORT}")
        
        chunk_count = 0 # Contador global para rastrear pacotes enviados
        
        # Loop externo: Mantém o servidor vivo para aceitar novas conexões
        while True:
            try:
                conn, addr = s.accept()
                print(f"[*] Cliente conectado: {addr}")
                
                with conn:
                    # Loop interno: Processa os múltiplos pedidos de chunks do mesmo cliente
                    while True:
                        # Aguarda a requisição HTTP/DASH simulada do cliente
                        req = conn.recv(1024)
                        if not req: 
                            break # Cliente fechou a conexão
                        
                        # =====================================================================
                        # BLOCO 4: EMPACOTAMENTO E ENVIO (PROTOCOLO DE APLICAÇÃO)
                        # Adiciona o Número de Sequência para telemetria e monta o chunk
                        # =====================================================================
                        # Cria um cabeçalho exato de 8 bytes (Ex: "00000042")
                        header = f"{chunk_count:08d}".encode('utf-8')
                        
                        # Processa pedido de ALTA QUALIDADE
                        if b"GET_CHUNK_HIGH" in req:
                            # Concatena o cabeçalho + "Lixo de Memória" (b'H') até dar exatamente 1MB
                            payload = header + (b'H' * (CHUNK_HIGH_SIZE - 8))
                            conn.sendall(payload)
                            chunk_count += 1
                            
                        # Processa pedido de BAIXA QUALIDADE
                        elif b"GET_CHUNK_LOW" in req:
                            # Concatena o cabeçalho + "Lixo de Memória" (b'L') até dar exatamente 250KB
                            payload = header + (b'L' * (CHUNK_LOW_SIZE - 8))
                            conn.sendall(payload)
                            chunk_count += 1
                            
            except KeyboardInterrupt:
                print("\n[*] Desligamento manual do servidor DASH.")
                break
            except Exception as e:
                # Silencia falhas de quebra de pipe (comum quando o cliente é morto pelo orquestrador)
                pass

if __name__ == '__main__':
    main()
