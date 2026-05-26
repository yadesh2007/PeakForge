(function setupPeakForgeToasts() {
  const DEFAULT_DURATION = 4000;

  function getContainer() {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.setAttribute("aria-live", "polite");
      container.setAttribute("aria-label", "Notifications");
      document.body.append(container);
    }
    return container;
  }

  function removeToast(toast) {
    toast.classList.add("is-hiding");
    window.setTimeout(() => toast.remove(), 220);
  }

  window.showToast = function showToast(message) {
    if (!message) {
      return null;
    }

    const toast = document.createElement("div");
    toast.className = "toast-message";
    toast.setAttribute("role", "status");
    toast.textContent = message;

    getContainer().append(toast);
    window.setTimeout(() => removeToast(toast), DEFAULT_DURATION);
    return toast;
  };

  window.showMessage = window.showToast;

  function showPayloadToast(payload) {
    if (typeof payload === "string") {
      window.showToast(payload);
      return;
    }

    if (payload && typeof payload === "object") {
      window.showToast(payload.message || payload.text || payload.detail);
    }
  }

  function bindSocket(socket) {
    if (!socket || typeof socket.on !== "function" || socket.__peakForgeToastsBound) {
      return;
    }

    socket.__peakForgeToastsBound = true;
    socket.on("toast", showPayloadToast);
    socket.on("notification", showPayloadToast);
    socket.on("message_sent", (payload) => showPayloadToast(payload || "Message sent"));
    socket.on("message_received", showPayloadToast);
    socket.on("chat_message", showPayloadToast);
    socket.on("connect_error", () => window.showToast("Real-time connection failed"));
  }

  window.PeakForgeToasts = {
    bindSocket,
    show: window.showToast,
  };

  document.addEventListener("DOMContentLoaded", () => {
    const flashScript = document.getElementById("flask-flashes");
    if (flashScript?.textContent) {
      JSON.parse(flashScript.textContent).forEach(([_type, message]) => {
        window.showToast(message);
      });
    }

    if (window.socket) {
      bindSocket(window.socket);
    }
  });

  document.addEventListener("peakforge:toast", (event) => {
    showPayloadToast(event.detail);
  });
})();
