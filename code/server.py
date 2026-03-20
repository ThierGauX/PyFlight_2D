import socket
import json
import time
import threading

# Configuration du serveur UDP
HOST = "0.0.0.0"  # Écoute sur toutes les interfaces
PORT = 5555

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"[SERVEUR] PyFlight 2D Multiplayer Server demarre sur le port {PORT} (UDP)")

    players = {}
    last_seen = {}

    timeout_duration = 5.0  # Expulser un joueur s'il ne donne pas de nouvelles pendant 5s

    def cleanup_inactive_players():
        while True:
            time.sleep(2)
            current_time = time.time()
            to_remove = []
            for addr, t in last_seen.items():
                if current_time - t > timeout_duration:
                    to_remove.append(addr)
            for addr in to_remove:
                print(f"[SERVEUR] Déconnexion pour inactivité : {players[addr].get('pseudo', 'Inconnu')} {addr}")
                del players[addr]
                del last_seen[addr]

    cleanup_thread = threading.Thread(target=cleanup_inactive_players, daemon=True)
    cleanup_thread.start()

    while True:
        try:
            data, addr = server_socket.recvfrom(2048)  # 2KB buffer par paquet UDP
            packet = json.loads(data.decode('utf-8'))
            
            # Formats attendus:
            # { "pseudo": "Bob", "x": 100, "y": -500, "angle": 0, "aircraft": "cessna" }
            
            players[addr] = packet
            last_seen[addr] = time.time()

            # Préparer la réponse avec tous les autres joueurs
            other_players = {}
            for p_addr, p_data in players.items():
                if p_addr != addr:
                    # On utilise l'ip:port comme clé unique pour identifier les autres
                    unique_id = f"{p_addr[0]}:{p_addr[1]}"
                    other_players[unique_id] = p_data

            response = json.dumps(other_players).encode('utf-8')
            server_socket.sendto(response, addr)

        except Exception as e:
            # Les erreurs de parse JSON ou sockets sont ignorées pour ne pas planter le serveur
            print(f"[SERVEUR] Erreur: {e}")

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SERVEUR] Arrêt du serveur.")
