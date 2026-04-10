<p align="center">
  <img src="logos/entropy-logo.png" width="120" alt="Escudo Anónimo logo" />
</p>

<h1 align="center">Escudo Anónimo</h1>

<p align="center">
  Aplicación de escritorio para Linux que rutea tu tráfico de red a través de Tor, DNSCrypt e I2P.<br>
  Desarrollado con Python y PyQt6.
</p>

<p align="center">
  <a href="https://agdalasv.github.io/escudo-anonimo/">
    <img src="https://img.shields.io/badge/Descargar-4BBA7E?style=for-the-badge" alt="Descargar">
  </a>
</p>

---

Una interfaz gráfica para controlar cada capa de privacidad, monitorear actividad en tiempo real y configurar los servicios sin tocar archivos de configuración manualmente.

---

## Capturas de pantalla

| Desconectado | Conectado |
|-------------|----------|
| ![](screenshots/disconnected.png) | ![](screenshots/connected.png) |

---

## Qué hace

- **Tor**: Ruta todo el tráfico TCP a través de la red Tor mediante proxy transparente. Tu IP real permanece oculta.
- **DNSCrypt**: Encripta y autentica todas las consultas DNS para que tu ISP no pueda ver qué dominios resuelves.
- **I2P**: Conecta a la red anónima I2P via i2pd. Útil para acceder a servicios internos (.i2p).
- **Block**: Bloquea sitios web no deseados con protección por contraseña.

Puedes habilitar cualquier combinación. Al presionar Conectar, la aplicación aplica reglas de firewall (nftables o iptables) e inicia los servicios seleccionados. Al presionar Desconectar, todo se revierte y el tráfico fluye normalmente.

La aplicación debe ejecutarse como root porque modifica reglas de firewall y configuración de red. Usa `pkexec` (Polkit) para pedir tu contraseña.

---

## Distribuciones soportadas

| Distribución | Instalador |
|---|---|
| Debian, Ubuntu y derivados | `installers/install-debian.sh` |
| Fedora, RHEL, CentOS Stream | `installers/install-fedora.sh` |
| Arch Linux, Manjaro, Endeavour | `installers/install-arch.sh` |
| NixOS | `installers/install-nixos.sh` |

---

## Requisitos

### Todas las distribuciones
- Python 3.10 o superior
- PyQt6
- Tor
- dnscrypt-proxy
- i2pd
- nftables o iptables
- Polkit (pkexec)

Los instaladores manejan todo automáticamente.

### NixOS only
- Se recomienda una entrada `services.tor.enable = true` en tu `configuration.nix`.

---

## Instalación

### Descargar

[Descarga el código aquí](https://agdalasv.github.io/escudo-anonimo/)

O clona el repositorio:
```bash
git clone https://github.com/agdalasv/escudo-anonimo.git
cd escudo-anonimo
```

---

### Debian / Ubuntu

```bash
sudo bash installers/install-debian.sh
```

El script:
1. Ejecuta `apt-get update` e instala los paquetes requeridos
2. Copia la aplicación a `/opt/escudo-anonimo`
3. Crea el launcher `/usr/local/bin/escudo-anonimo`
4. Instala el archivo desktop y el icono
5. Crea una política Polkit

---

### Fedora

```bash
sudo bash installers/install-fedora.sh
```

El script:
1. Instala paquetes vía `dnf`
2. Copia la aplicación a `/opt/escudo-anonimo`
3. Crea el launcher, desktop e icono
4. Crea una política Polkit
5. Aplica contexto SELinux si está activo

---

### Arch Linux

```bash
sudo bash installers/install-arch.sh
```

El script:
1. Instala paquetes vía `pacman`
2. Copia la aplicación a `/opt/escudo-anonimo`
3. Crea el launcher, desktop e icono
4. Crea una política Polkit

---

### NixOS

```bash
sudo bash installers/install-nixos.sh
```

NixOS es diferente porque el sistema se maneja declarativamente.

El script:
1. Detiene y deshabilita instancias conflictivas
2. Copia la aplicación a `/opt/escudo-anonimo`
3. Escribe `/etc/nixos/escudo-anonimo.nix`
4. Modifica `/etc/nixos/configuration.nix`
5. Ejecuta `nixos-rebuild switch`

---

## Cómo usar

1. Abre la aplicación.
2. En la ventana principal, usa los interruptores en cada tarjeta para seleccionar las capas que quieres habilitar.
3. Presiona **Conectar**. El anillo de estado se vuelve verde cuando está activo.
4. Para verificar: abre un test de DNS leak y ejecuta una prueba extendida.
5. Presiona **Desconectar** para detener todo y quitar las reglas de firewall.

### Combinaciones de capas

- **Solo Tor**: Todo el tráfico TCP va por Tor. DNS se resuelve anónimamente.
- **Solo DNSCrypt**: Consultas DNS encriptadas. TCP usa tu IP real.
- **Tor + DNSCrypt**: Máxima privacidad.
- **I2P**: Inicia i2pd y configura el proxy HTTP a `127.0..1:4444`.

---

## Configuración

Haz clic en el botón de engranaje para abrir el panel de ajustes:

- **Tor**: TransPort, DNSPort, SocksPort, nodos de salida, StrictNodes
- **DNSCrypt**: puerto, DNSSEC, no-log, no-filter
- **I2P**: puertos HTTP/SOCKS, ancho de banda
- **Theme**: oscuro o claro

Los ajustes se guardan en `~/.config/escudo-anonimo/config.json`.

---

## Cómo funciona internamente

### Firewall

Al conectar, la aplicación escribe reglas usando nftables (preferido) o iptables como respaldo.

Para proxy transparente de Tor, se crea una tabla `ip escudo-anonimo` con una cadena `nat output` que:
- Retorna tráfico del proceso Tor mismo (para evitar bucles)
- Retorna tráfico hacia redes locales
- Redirige todo DNS (puerto 53) al DNSPort de Tor o dnscrypt-proxy
- Redirige todos los paquetes TCP SYN al TransPort de Tor

Al desconectar, la tabla `escudo-anonimo` se elimina completamente.

### DNS en NixOS

Si `systemd-resolved` está corriendo, la aplicación lo configura vía `resolvectl` para rutear todas las consultas a través del servicio activo.

---

## Desinstalación

### Debian / Fedora / Arch

```bash
sudo rm -rf /opt/escudo-anonimo
sudo rm -f /usr/local/bin/escudo-anonimo
sudo rm -f /usr/share/applications/escudo-anonimo.desktop
sudo rm -f /usr/share/pixmaps/escudo-anonimo.png
sudo rm -f /usr/share/icons/hicolor/256x256/apps/escudo-anonimo.png
sudo rm -f /usr/share/polkit-1/actions/org.escudoanonimo.policy
```

### NixOS

1. Remueve `escudo-anonimo.nix` de los `imports` en `/etc/nixos/configuration.nix`
2. Elimina el archivo de modulo: `sudo rm /etc/nixos/escudo-anonimo.nix`
3. Elimina la aplicación: `sudo rm -rf /opt/escudo-anonimo`
4. Ejecuta `sudo nixos-rebuild switch`

---

## Solución de problemas

### La aplicación no aparece en el menú (NixOS)

Ejecuta `kbuildsycoca6 --noincremental` como usuario normal.

### "tor no está instalado" o "dnscrypt-proxy no está instalado"

El binario no está en PATH. En NixOS, ejecuta `sudo nixos-rebuild switch`. En otras distribuciones, vuelve a correr el instalador.

### El tráfico no parece pasar por Tor

Verifica que las reglas de firewall estén activas: `sudo nft list table ip escudo-anonimo`. Revisa el log de actividad en la aplicación.

### El diálogo de privilegios no aparece

Asegúrate que Polkit esté corriendo: `systemctl status polkit`.

---

## Estructura del proyecto

```
escudo-anonimo/
  main.py                  Punto de entrada.
  logos/
    entropy-logo.png       Icono de la app.
  core/
    config.py              Configuración JSON.
    connection.py          Orquestador de capas.
    firewall.py           Reglas nftables/iptables.
    tor.py                Servicio Tor.
    dnscrypt.py            Servicio DNSCrypt.
    i2p.py                 Servicio I2P.
    blocker.py             Bloqueador de sitios.
    platform.py            Detección de SO.
  gui/
    main_window.py         Ventana principal.
    widgets.py            Componentes personalizados.
    themes.py             Temas oscuro/claro.
    settings_panel.py      Panel de ajustes.
  installers/             Scripts de instalación.
```

---

## Apoyar el proyecto

Invita una taza de café ☕

**BTC:** `3L8f3v6BWwL7KBcb8AMZQ2bpE3ACne2EUf`

---

## Reportar bugs

¿Encontraste un bug? Escríbenos: **agdala.sv@gmail.com**

---

## Licencia

MIT License - 2026 Agdala