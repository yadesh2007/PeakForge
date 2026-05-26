document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector("[data-image-input]");
  const preview = document.querySelector("[data-image-preview]");
  const fallback = document.querySelector("[data-image-preview-fallback]");

  if (!input || !preview) {
    return;
  }

  input.addEventListener("change", () => {
    const file = input.files && input.files[0];
    if (!file) {
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    preview.src = previewUrl;
    preview.hidden = false;
    if (fallback) {
      fallback.hidden = true;
    }
    preview.addEventListener("load", () => URL.revokeObjectURL(previewUrl), { once: true });
  });
});
