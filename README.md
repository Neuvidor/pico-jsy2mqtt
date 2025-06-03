# pico-jsy2mqtt

Passerelle de télémétrie basée sur Raspberry Pi Pico, pour publier les mesures du module JSY-MK-194G (via Modbus RTU) vers un serveur MQTT.

## 🔧 Fonctionnalités

- 💬 Lecture des données Modbus RTU depuis le module **JSY-MK-194G**
- 📡 Publication automatique vers un broker **MQTT**
- 🔄 Détection automatique du baudrate et de l’ID Modbus
- 🔍 Évitement des publications redondantes
- 🔔 Indication d’état système via la **LED du Raspberry Pico**
- ⚙️ Paramétrage centralisé dans `config.py`

## 🧱 Architecture des fichiers

```
├── boot.py            # Initialisation UART et LED au boot
├── main.py            # Boucle principale : WiFi, MQTT, lecture + publication
├── modbus_lib.py      # Gestion du protocole Modbus RTU (JSY-MK-194G)
├── config.py          # Paramètres WiFi, MQTT, UART, debug, etc.
```

## ⚡ Matériel requis

- 1 × Raspberry Pi **Pico** ou **Pico W** (version WiFi)
- 1 × Module **JSY-MK-194G**
- Connexion UART via GPIO :
  - **TX Pico → RX JSY** (par défaut GPIO 0)
  - **RX Pico ← TX JSY** (par défaut GPIO 1)
- Broker MQTT accessible sur le réseau (ex : Mosquitto)

## 🐍 Mise en route

### 1. 📥 Flasher MicroPython sur le Pico

1. Télécharger le firmware depuis [micropython.org](https://micropython.org/download/rp2-pico-w/)
2. Brancher le Pico tout en appuyant sur le bouton **BOOTSEL**
3. Le Pico apparaît comme un disque USB
4. Copier le fichier `.uf2` dans ce disque → redémarrage automatique

### 2. 📁 Transférer les fichiers

Utilise **Thonny** pour copier l'ensemble des données du dossier **source**

### 3. ⚙️ Modifier les paramètres

Édite le fichier `config.py` pour définir :
- Le **SSID** et **mot de passe** WiFi
- Les **identifiants MQTT**
- Le **port**, le **client name**, et le topic de base

## 🔎 Données publiées

Chaque donnée est publiée sous la forme :
```
JSY-MK-194G/ch1_voltage → 231.4
JSY-MK-194G/ch1_power   → -420
...
```

## 💡 Comportement de la LED

| Phase              | État de la LED                   |
|--------------------|----------------------------------|
| Boot               | Allumée 2 s, puis éteinte        |
| Connexion WiFi     | Clignotement lent 1 Hz           |
| Connexion MQTT     | Clignotement lent 1 Hz           |
| Connexion réussie  | 3 clignotements rapides + fixe 1 s + OFF |
| Fonctionnement     | Allumée fixe                     |
| Publication MQTT   | Extinction 50 ms puis allumée    |


## 🧰 Dépendances MicroPython

Assure-toi que les modules suivants sont disponibles :
- `umqtt.simple`
- `ustruct`
- `network`
- `machine`
- `time`

Utilisables nativement avec MicroPython 1.20+ sur Raspberry Pi Pico W.

## 📄 Licence

Projet open-source sous licence MIT.

## 👤 Auteur

Neuvidor