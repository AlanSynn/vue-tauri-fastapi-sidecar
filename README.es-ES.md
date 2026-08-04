

<div align="center">
  <img src="extras/alan-standing.png" alt="Logo Alan Standing" width="150">
  <h1>vue-tauri-fastapi-sidecar</h1>
  <p>Tauri con Vite-Vue utilizando un sidecar de Python</p>
</div>


<div align="center">

<!-- Opcional: Enlace a tus lanzamientos si están disponibles -->
<!-- [Descarga la aplicación de ejemplo y pruébala](https://github.com/AlanSynn/vue-tauri-fastapi-sidecar/releases) -->

![Python](https://img.shields.io/badge/-Python-000?&logo=Python)
![TypeScript](https://img.shields.io/badge/-TypeScript-000?&logo=TypeScript)
![JavaScript](https://img.shields.io/badge/-JavaScript-000?&logo=JavaScript)
![Rust](https://img.shields.io/badge/-Rust-000?&logo=Rust)
![FastAPI](https://img.shields.io/badge/-FastAPI-000?&logo=fastapi)
![Vue.js](https://img.shields.io/badge/-Vue.js-000?&logo=vuedotjs)
![Vite](https://img.shields.io/badge/-Vite-000?&logo=vite&logoColor=purple)
![Tauri](https://img.shields.io/badge/-Tauri-000?&logo=Tauri)
</div>

Una aplicación nativa construida con Tauri v2 que genera un subproceso de Python (sidecar) el cual inicia un servidor FastAPI. Este proyecto utiliza Vue.js (con Vite) para el frontend.



> [!NOTE]
> Este proyecto está fuertemente inspirado en [dieharders/example-tauri-v2-python-server-sidecar](https://github.com/dieharders/example-tauri-v2-python-server-sidecar). Las diferencias clave incluyen el uso de Vue.js y Vite para el frontend (con un enfoque en las convenciones estrictas de Vite), la utilización de FastAPI como backend y la adopción de `uv` para gestionar todas las tareas relacionadas con la compilación de Python.



## Tabla de Contenidos

- [Tabla de Contenidos](#table-of-contents)
- [Introducción](#introduction)
- [Cómo Funciona](#how-it-works)
- [Características](#features)
- [Estructura del Proyecto](#project-structure)
- [Primeros Pasos](#getting-started)
  - [Dependencias](#dependencies)
  - [Ejecutar](#run)
- [Desplegar usando tu máquina](#deploy-using-your-machine)
  - [1. Compilar el sidecar de Python](#1-compile-python-sidecar)
  - [2. Compilar el Frontend de Vue.js](#2-build-vuejs-frontend)
  - [3. Compilar la Aplicación Tauri](#3-build-tauri-app)
- [Desplegar usando GitHub Actions](#deploy-using-github-actions)
- [Tareas Pendientes](#todos)
- [Aprende Más](#learn-more)

## Introducción

Esta aplicación de ejemplo utiliza Vue.js (impulsado por Vite) como frontend y Python (FastAPI) como backend. Tauri es un framework de Rust que orquesta el frontend y los backends en una experiencia de aplicación nativa.

Este proyecto plantilla está diseñado para demostrar el uso de ejecutables de Python de archivo único con Tauri v2, específicamente integrados con un frontend basado en Vite.

![captura de pantalla de la aplicación](extras/screenshot.png "captura de pantalla de la aplicación")

Los "sidecars" de Tauri permiten a los desarrolladores empaquetar dependencias para facilitar la instalación al usuario. La API de Tauri permite que el frontend se comunique con cualquier runtime y le dé acceso al disco del sistema operativo, cámara y otras funciones de hardware nativo. Esto se define en el archivo `tauri.conf.json`. Consulta [aquí](https://v2.tauri.app/develop/sidecar/) para más información.

## Cómo Funciona

<div align="center">
  <img src="extras/diagram.svg" alt="arquitectura del sidecar de Python" title="arquitectura del sidecar de Python" height="600"/>
</div>

> [!NOTE]
> Esta sección proporciona una visión general adaptada de proyectos similares. Algunos detalles podrían variar ligeramente. Consulta `package.json` para los comandos de compilación exactos y `src-tauri/src/main.rs` para la lógica precisa de gestión del sidecar.

- **Frontend:** Tauri muestra la interfaz de usuario del frontend, construida con Vue.js y Vite, dentro de un webview nativo. Este enfoque resulta en paquetes de aplicación más pequeños en comparación con soluciones como Electron, ya que utiliza el motor webview existente del sistema operativo.

- **Sidecar del Backend:** El backend de Python, utilizando el framework FastAPI (`src/backends/main.py`), se compila en un ejecutable de archivo específico para la plataforma usando PyInstaller. Este proceso es manejado por scripts en `package.json` (ej. `pnpm build:sidecar-winos`, `pnpm build:sidecar-macos-all`, `pnpm build:sidecar-linux`) que colocan el ejecutable (ej. `main-x86_64-pc-windows-msvc`, `main-x86_64-apple-darwin`, `main-aarch64-apple-darwin`) en el directorio `src-tauri/bin/api/`.

- **Generación y Comunicación:** El proceso principal de Rust de Tauri (`src-tauri/src/main.rs`) está configurado (en `tauri.conf.json`) para iniciar el ejecutable del sidecar de Python correspondiente cuando la aplicación se inicia. El sidecar inicia un servidor FastAPI (generalmente en `localhost:8008`). El frontend de Vue.js se comunica con el sidecar principalmente mediante solicitudes HTTP a este servidor local. Tauri gestiona el ciclo de vida del sidecar, asegurando que se inicie con la aplicación y manejando potencialmente señales de apagado. Si bien la comunicación principal de datos es por HTTP, Tauri podría usar stdin/stdout para comandos básicos de ciclo de vida con el proceso del sidecar en sí.

- **Compilaciones Multiplataforma:** El proyecto incluye comandos de compilación separados para diferentes sistemas operativos y arquitecturas (Windows, Linux, macOS x86_64, macOS ARM64) para garantizar que se empaquete el sidecar correcto. El comando `pnpm build:sidecar-macos-all` simplifica la creación de una compilación universal para macOS compilando ambas arquitecturas.

- **Desarrollo:** Durante el desarrollo (`pnpm tauri dev`), Tauri generalmente ejecuta el frontend a través del servidor de desarrollo de Vite y gestiona el proceso del sidecar según la configuración.

- **Flujo de trabajo simplificado:** Si no te sientes cómodo programando en Rust, esta configuración te permite concentrarte principalmente en la interacción del frontend (Vue.js) y la API del backend (Python/FastAPI) a través de solicitudes HTTP estándar.

- **Apagado:** Cuando se cierra la ventana principal de la aplicación, Tauri se asegura de que el servidor FastAPI y el proceso del sidecar de Python se cierren correctamente.

## Características

Esto debería darte todo lo que necesitas para construir una aplicación nativa local que pueda usar otros programas para realizar trabajo especializado (como un servidor, motor LLM o base de datos).

- Inicia y comunícate con cualquier binario o runtime escrito en cualquier lenguaje. Este ejemplo usa un ejecutable de Python.

- Comunicación entre el frontend (JavaScript) y el servidor backend (Python) mediante HTTP.

- Comunicación IPC entre el frontend (JavaScript) y el framework Tauri (Rust).

- También controla esta aplicación desde una fuente de interfaz de usuario externa como otro sitio web, aplicación o terminal. Siempre que use http(s) y agregues la URL a la lista blanca en la configuración del servidor `main.py`.

## Estructura del Proyecto

Estas son las carpetas importantes del proyecto que debes entender.

```bash
/app # (código frontend - Vue.js/Vite: componentes, main.js, App.vue, etc.)
/public # (activos estáticos servidos por Vite)
/src/backends # (código backend, el "sidecar")
/src-tauri
  |  /bin/api # (aquí se coloca el sidecar compilado)
  |  /icons # (los iconos de la aplicación van aquí)
  |  /src/main.rs # (lógica principal de la app Tauri)
  |  tauri.conf.json # (archivo de configuración de Tauri para permisos de la app, etc.)
package.json # (scripts de compilación)
```

## Primeros Pasos

### Dependencias

Instala todas las dependencias tanto para el frontend (JavaScript/Node) como para el backend (Python):

```bash
# Recomendado: Instala dependencias de Node y Python
pnpm install-reqs
```

Alternativamente, puedes instalarlas por separado:

```bash
# Instalar solo dependencias frontend (Node.js)
pnpm install

# Instalar solo dependencias backend (Python) usando uv
# Asume que tienes uv instalado (pipx install uv)
# Lee las dependencias de pyproject.toml
uv pip install .
```

Tauri requiere iconos en la carpeta correspondiente. Ejecuta el script para generar automáticamente iconos desde una imagen de origen. He incluido iconos por conveniencia.

```bash
pnpm build:icons
```

### Ejecutar

Ejecuta la aplicación en modo de desarrollo:

```bash
pnpm tauri dev
```

## Desplegar usando tu máquina

### 1. Compilar el sidecar de Python

Ejecuta esto al menos una vez antes de ejecutar `pnpm tauri dev` o `pnpm tauri build` y cada vez que realices cambios en tu código de Python:

```bash
pnpm build:sidecar-winos
# O
pnpm build:sidecar-macos-all # Crea un binario universal para x86_64 y aarch64 de macOS
# O
pnpm build:sidecar-linux
```

En caso de que no tengas PyInstaller instalado, ejecuta:

```
pip install -U pyinstaller
```

Una nota sobre la compilación del exe de Python (la bandera -F empaqueta todo en un solo .exe). No necesitarás ejecutar esto manualmente en cada compilación, lo he incluido en los scripts de compilación.

### 2. Compilar el Frontend de Vue.js

Compila los activos estáticos del frontend usando Vite. Este paso generalmente se maneja automáticamente mediante el comando `pnpm tauri build` a través de `beforeBuildCommand` en `tauri.conf.json`, pero se puede ejecutar manualmente:

```bash
pnpm build
```

### 3. Compilar la Aplicación Tauri

Tauri ejecuta el comando de compilación del frontend (`pnpm build` por defecto en `tauri.conf.json`) antes de empaquetar la aplicación.
Compila la aplicación de producción en tu máquina para un sistema operativo específico:

```bash
pnpm tauri build
```

Esto crea un instalador ubicado aquí:

- `<project-dir>\src-tauri\target\release\bundle\nsis`

Y el ejecutable crudo aquí:

- `<project-dir>\src-tauri\target\release`

## Desplegar usando GitHub Actions

Haz un fork de este repositorio para acceder a un disparador manual que compile para cada plataforma (Windows, MacOS, Linux) y cargue una versión.

Luego, puedes modificar el archivo `release.yml` para adaptarlo a las necesidades de la pipeline de compilación de tu aplicación específica. Los permisos del workflow deben establecerse en "Lectura y escritura". Cualquier etiqueta git creada antes de que existiera un workflow no será utilizable para ese workflow. Debes especificar una etiqueta desde la cual ejecutar (no un nombre de rama).

Iniciar el Workflow Manualmente:

1. Navega a la pestaña "Actions" (Acciones) en tu repositorio de GitHub.
2. Selecciona el workflow "Manual Tauri Release".
3. Haz clic en "Run workflow" (Ejecutar workflow) y proporciona los parámetros necesarios:

   - release_name: El título de la versión.
   - release_notes (opcional): Notas o registro de cambios para la versión.
   - release_type: ("draft", "public", "private")

## Tareas Pendientes

- Ejemplo de endpoint de API que demuestra el manejo de rutas de archivos para archivos `--add-data` y el uso de `sys._MEIPASS` para encontrar la ruta relativa al ejecutable de producción.

- Pasar parámetros al sidecar (como el puerto del servidor) a través de un formulario del frontend.

- Pasar el argumento `--dev-sidecar` al script `pnpm tauri dev` que indica a Tauri que ejecute los sidecars en "modo dev". Esto permitiría ejecutar el código de Python desde el intérprete instalado en tu máquina en lugar de tener que compilar manualmente con `pnpm build:sidecar-[os]` cada vez que realices cambios en el código Python.

- Desarrollar un gestor independiente de múltiples sidecars que pueda manejar el inicio/apagado y la comunicación entre todos los demás sidecars generados en la aplicación.

## Aprende Más

- [Tauri Framework](https://tauri.app/) - aprende sobre el desarrollo de aplicaciones nativas en JavaScript y Rust.
- [Vue.js](https://vuejs.org/guide/introduction.html) - aprende sobre el framework progresivo de JavaScript.
- [Vite](https://vitejs.dev/guide/) - aprende sobre las herramientas para frontend.
- [FastAPI](https://fastapi.tiangolo.com/) - aprende sobre las características del servidor y la API de FastAPI.
- [PyInstaller](https://pyinstaller.org/en/stable/) - aprende sobre el empaquetado de código Python.
