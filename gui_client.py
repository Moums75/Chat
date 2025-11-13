import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ChatGUI:
    def __init__(self):
        # ===== Fenêtre principale =====
        self.root = tk.Tk()
        self.root.title("Chat - Client (GUI)")  # <- regarde le titre !
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        self.root.configure(bg="#f5f5f5")

        self.socket = None
        self.listening = False
        self.username = None

        # ======= ZONE CONNEXION (haut) =======
        self.header = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        self.header.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.header, text="Pseudo :", bg="#ffffff").pack(side=tk.LEFT, padx=5, pady=10)
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.header, textvariable=self.username_var, width=15)
        self.username_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.header, text="Serveur :", bg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.server_var = tk.StringVar(value="127.0.0.1")
        self.server_entry = tk.Entry(self.header, textvariable=self.server_var, width=12)
        self.server_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.header, text="Port :", bg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar(value="59001")
        self.port_entry = tk.Entry(self.header, textvariable=self.port_var, width=6)
        self.port_entry.pack(side=tk.LEFT, padx=5)

        self.connect_button = tk.Button(
            self.header,
            text="Connexion",
            bg="#3b82f6",
            fg="white",
            command=self.connect_to_server,
        )
        self.connect_button.pack(side=tk.RIGHT, padx=10)

        # ======= ZONE MESSAGES (milieu) =======
        center = tk.Frame(self.root, bg="#f5f5f5")
        center.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.text_area = scrolledtext.ScrolledText(
            center,
            state="disabled",
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            relief="solid",
            bd=1,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # ======= ZONE SAISIE (bas) =======
        bottom = tk.Frame(self.root, bg="#f5f5f5")
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entry_message = tk.Entry(
            bottom,
            font=("Segoe UI", 11),
            bg="#ffffff",
            relief="solid",
            bd=1,
        )
        self.entry_message.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_message.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            bottom,
            text="Envoyer",
            bg="#3b82f6",
            fg="white",
            command=self.send_message,
            width=10,
        )
        self.send_button.pack(side=tk.LEFT, padx=(10, 0))

        # Au début on ne peut pas envoyer tant qu'on n'est pas connecté
        self.entry_message.config(state="disabled")
        self.send_button.config(state="disabled")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    # ========== Connexion au serveur ==========
    def connect_to_server(self):
        username = self.username_var.get().strip()
        server = self.server_var.get().strip()
        port_str = self.port_var.get().strip()

        if not username:
            messagebox.showerror("Erreur", "Merci de choisir un pseudo.")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Erreur", "Le port doit être un nombre.")
            return

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server, port))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de se connecter : {e}")
            return

        self.username = username

        # Envoie "USERNAME <pseudo>" comme ton client en console
        self.send_raw(f"USERNAME {self.username}")

        # On lance l'écoute des messages
        self.listening = True
        threading.Thread(target=self.listen_loop, daemon=True).start()

        # Affiche info et active la zone d'envoi
        self.add_message(f"✅ Connecté au serveur en tant que {self.username}")
        self.entry_message.config(state="normal")
        self.send_button.config(state="normal")

        # On enlève la zone de connexion comme tu voulais
        self.header.destroy()

    # ========== Réception ==========
    def listen_loop(self):
        while self.listening:
            data = ""
            try:
                data = self.socket.recv(1024).decode("UTF-8")
            except socket.error:
                break

            if not data or data == "QUIT":
                break

            self.add_message(data)
            time.sleep(0.1)

        self.add_message("❌ Déconnecté du serveur.")
        self.tidy_up()

    # ========== Envoi ==========
    def send_raw(self, msg: str):
        try:
            self.socket.sendall(msg.encode("UTF-8"))
        except socket.error:
            self.add_message("⚠️ Erreur d'envoi (socket)")

    def send_message(self, event=None):
        if not self.socket:
            return

        message = self.entry_message.get().strip()
        if message == "":
            return

        full_message = f"{self.username}: {message}"
        self.send_raw(full_message)
        self.entry_message.delete(0, tk.END)

    # ========== Affichage ==========
    def add_message(self, msg: str):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)

    # ========== Fermeture ==========
    def tidy_up(self):
        self.listening = False
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        self.socket = None

    def on_close(self):
        self.listening = False
        try:
            if self.socket:
                self.send_raw("QUIT")
                self.socket.close()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    ChatGUI()
