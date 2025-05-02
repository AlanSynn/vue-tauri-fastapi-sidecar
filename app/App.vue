<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';

// Constants
const DOCS_URL = "https://github.com/AlanSynn/vue-tauri-fastapi-sidecar";
const DOMAIN = "localhost";
const PORT = "8008";

// State
interface Status {
  connected: boolean;
  info: string;
}
const status = ref<Status>({ connected: false, info: "" });
const logs = ref<string>("[ui] Listening for sidecar & network logs...");

// Computed styles based on state
const connectButtonClasses = computed(() => {
  const base = ['action-button', 'connect-button-style'];
  if (status.value.connected) {
    base.push('connected');
  }
  return base;
});

// Tauri event listeners cleanup function type
type CleanupFunction = () => void;
let cleanupListeners: CleanupFunction | null = null;

// Methods
const initSidecarListeners = async () => {
  const unlistenStdout = await listen<string>('sidecar-stdout', (event) => {
    console.log('Sidecar stdout:', event.payload);
    if (event.payload?.length > 0 && event.payload !== "\r\n") {
      logs.value += `\n${event.payload}`;
    }
  });

  const unlistenStderr = await listen<string>('sidecar-stderr', (event) => {
    console.error('Sidecar stderr:', event.payload);
    if (event.payload?.length > 0 && event.payload !== "\r\n") {
      logs.value += `\n${event.payload}`;
    }
  });

  cleanupListeners = () => {
    unlistenStdout();
    unlistenStderr();
  };
};

const apiAction = async (endpoint: string, method: string = 'GET', payload?: any): Promise<any> => {
  const url = `http://${DOMAIN}:${PORT}/${endpoint}`;
  try {
    const body = payload ? JSON.stringify(payload) : null;
    const headers = {
      "Content-Type": "application/json",
    };

    const res = await fetch(url, { method, headers, body });
    if (!res.ok) {
      throw new Error(`Response status: ${res.status} ${await res.text()}`);
    }
    const json = await res.json();
    console.log(json);
    if (json?.message) {
      logs.value += `\n[server-response] ${json.message}`;
    }
    return json;
  } catch (err: any) {
    console.error(`[server-response] ${err}`);
    logs.value += `\n[server-response] ${err}`;
    throw err; // Re-throw to indicate failure
  }
};

const connectServerAction = async () => {
  try {
    const result = await apiAction("v1/connect");
    if (result) {
      status.value = {
        connected: true,
        info: `Host: ${result.data.host}\nProcess id: ${result.data.pid}\nDocs: http://${result.data.host}:${PORT}/docs`, // Added port and protocol for docs
      };
    }
  } catch (err) {
    console.error(`[ui] Failed to connect to api server. ${err}`);
    logs.value += `\n[ui] Failed to connect to api server. Ensure the sidecar is running and the server started.`;
  }
};

const shutdownSidecarAction = async () => {
  try {
    const result = await invoke<boolean>("shutdown_sidecar");
    if (result) {
      status.value = {
        connected: false,
        info: "",
      };
      logs.value += '\n[ui] Sidecar shutdown requested.';
    } else {
      logs.value += '\n[ui] Sidecar shutdown command returned false.';
    }
  } catch (err) {
    console.error(`[ui] Failed to shutdown sidecar. ${err}`);
    logs.value += `\n[ui] Failed to shutdown sidecar: ${err}`;
  }
};

const startSidecarAction = async () => {
  try {
    await invoke("start_sidecar");
    logs.value += '\n[ui] Sidecar start requested. Attempting to connect...';
    // Optionally attempt to connect automatically after starting
    setTimeout(connectServerAction, 1000); // Delay to allow server to start
  } catch (err) {
    console.error(`[ui] Failed to start sidecar. ${err}`);
    logs.value += `\n[ui] Failed to start sidecar: ${err}`;
  }
};

const mockAPIAction = async () => {
  try {
    logs.value += '\n[ui] Sending mock API request...';
    await apiAction("v1/completions", "POST", { prompt: "An example query." });
  } catch (err) {
    console.error(`[ui] Failed to get mock completion. ${err}`);
    // Error is already logged by apiAction
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'F11') {
    event.preventDefault();
    invoke('toggle_fullscreen');
  }
};

// Lifecycle Hooks
onMounted(() => {
  initSidecarListeners();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  if (cleanupListeners) {
    cleanupListeners();
  }
  window.removeEventListener('keydown', handleKeydown);
  // Consider calling shutdownSidecarAction here if appropriate for the app lifecycle
  // shutdownSidecarAction();
});

</script>

<template>
  <!-- Header/Footer Container -->
  <header class="header-footer-container">
    <!-- About Section -->
    <section class="about-section">
      <p>
        Get started by editing
        <code class="font-mono font-bold">src-tauri/src/main.rs</code> and
        <code class="font-mono font-bold">src/backends/main.py</code>.
      </p>
      <a :href="DOCS_URL" target="_blank" rel="noopener noreferrer">
        Read the project docs
        <code class="font-mono font-bold text-yellow-300">here</code>
      </a>
    </section>
    <!-- Title and Logo Section -->
    <section class="title-logo-section">
      <div class="title-logo-content">
        <div>
          <a class="pointer-events-auto" href="https://sorob.net" target="_blank" rel="noopener noreferrer">
            Vue Tauri FastAPI Sidecar
            <br>
            by @AlanSynn
          </a>
          <a class="pointer-events-auto" href="https://www.svgbackgrounds.com" target="_blank" rel="noopener noreferrer">
            BG by svgbackgrounds.com
          </a>
        </div>
        <img
          src="/alan-standing.png"
          alt="App Logo"
          class="logo-image"
          width="50"
          height="50"
        />
      </div>
    </section>
  </header>

  <!-- Log Display Area -->
  <section aria-labelledby="log-title">
    <h2 id="log-title" class="sr-only">Application Logs</h2> <!-- Accessibility improvement -->
    <pre class="logs-display"><code>{{ logs }}</code></pre> <!-- Wrap logs in pre/code for semantics -->
  </section>

  <!-- Action Buttons Grid -->
  <section class="button-grid" aria-label="Actions">
    <!-- Connect to server button -->
    <button
      :class="connectButtonClasses"
      :disabled="status.connected"
      @click="connectServerAction"
    >
      <h2>
        {{ status.connected ? "Connected" : "Connect" }}
        <span>&rarr;</span>
      </h2>
      <p>
        {{ status.connected ? status.info : "Establish connection to API server." }}
      </p>
    </button>

    <!-- Mock API endpoint button -->
    <button
      class="action-button"
      @click="mockAPIAction"
      :disabled="!status.connected"
    >
      <h2>
        Test API <span>&rarr;</span>
      </h2>
      <p>
        Send a mock request to the completions endpoint.
      </p>
    </button>

    <!-- Start sidecar process button -->
    <button
      class="action-button"
      @click="startSidecarAction"
      :disabled="status.connected"
    >
      <h2>
        Start Sidecar <span>&rarr;</span>
      </h2>
      <p>
        Start the Python sidecar process.
      </p>
    </button>

    <!-- Shutdown sidecar process button -->
    <button
      class="action-button"
      @click="shutdownSidecarAction"
      :disabled="!status.connected"
    >
      <h2>
        Shutdown Sidecar <span>&rarr;</span>
      </h2>
      <p>
        Terminate the Python sidecar process.
      </p>
    </button>
  </section>

  <!-- Optional Spinning Background -->
  <!-- <div class="absolute flex justify-center items-center left-[50%] right-[50%] bottom-[50%] top-[50%] w-[0px] h-[0px] -z-10">
    <div class="relative w-[100vw] h-[100vw] bg-cover bg-fixed bg-center aspect-square animate-spin-slow"></div>
  </div> -->
</template>

<style scoped>
/* Scoped styles for App.vue specific adjustments */

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.logo-image {
  border-radius: 50%; /* Make logo circular */
  object-fit: cover;
  border: 2px solid var(--border-color);
}

/* Use <pre><code> for logs for better semantics */
.logs-display {
  line-height: 1.5; /* Adjust line height for logs */
}
.logs-display code {
  background-color: transparent; /* Remove double background */
  padding: 0;
  font-size: inherit; /* Inherit font size from pre */
}

.action-button p {
  color: rgba(var(--foreground-rgb), 0.65); /* Slightly dimmer description */
  font-size: 0.8rem;
}

/* Adjustments for connected button description */
.connect-button-style.connected p {
  font-size: 0.75rem; /* Smaller font for status info */
  color: rgba(var(--foreground-rgb), 0.8); /* Make status info slightly more prominent */
  line-height: 1.4;
}

@media (prefers-color-scheme: dark) {
  .action-button p {
    color: rgba(var(--foreground-rgb), 0.6);
  }
  .connect-button-style.connected p {
    color: rgba(var(--secondary-accent), 0.85);
  }
}

/* Optional: Add a subtle transition for the main app container */
#app {
  transition: background-color 0.3s ease;
}

/* Ensure pointer events are enabled for interactive elements */
.pointer-events-auto {
  pointer-events: auto;
}

/* Adjust button disabled style to match page.tsx */
.action-button:disabled {
  opacity: 0.6; /* Slightly less opaque than default */
  cursor: not-allowed;
}

.connect-button-style.disabled {
   border-style: dashed;
   opacity: 0.6;
   cursor: not-allowed;
}

.connect-button-style.disabled:hover {
    /* Prevent hover effects when disabled */
    border-color: transparent;
    background-color: transparent;
}

/* Ensure logo is visible in light/dark mode */
img.dark {
  /* Assuming logo.svg is designed for dark backgrounds,
     you might need filter adjustments for light mode */
}
@media (prefers-color-scheme: light) {
  img.dark {
    /* filter: invert(1) hue-rotate(180deg); */ /* Example filter */
  }
}
</style>
