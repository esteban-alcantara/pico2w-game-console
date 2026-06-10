# Estado global compartido entre el juego y el servidor WiFi

last_score = 0          # Puntuación de la última partida
current_game = "none"   # Juego activo actualmente ("none", "snake", etc.)
uptime_start = 0        # Se asigna en main.py con time.time()