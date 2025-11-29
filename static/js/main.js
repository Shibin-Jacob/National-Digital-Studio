document.addEventListener("DOMContentLoaded", () => {
    const animated = document.querySelectorAll(".fade-in, .slide-up");

    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("animate-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    animated.forEach(el => observer.observe(el));
});


    // Quantity +/- controls
    const qtyControls = document.querySelectorAll(".quantity-control");
    qtyControls.forEach(control => {
        const input = control.querySelector("input[type='number']");
        const buttons = control.querySelectorAll(".qty-btn");

        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                const action = btn.dataset.action;
                let value = parseInt(input.value || "1", 10);
                if (action === "inc") {
                    value += 1;
                } else if (action === "dec") {
                    value = Math.max(1, value - 1);
                }
                input.value = value;
            });
        });
    });

    // File upload – show selected file names
    const fileInput = document.getElementById("design_files");
    const fileList = document.getElementById("file-list");

    if (fileInput && fileList) {
        fileInput.addEventListener("change", () => {
            fileList.innerHTML = "";
            const files = Array.from(fileInput.files || []);
            if (!files.length) {
                return;
            }
            files.forEach(file => {
                const item = document.createElement("div");
                item.className = "file-list-item";

                const dot = document.createElement("span");
                dot.className = "file-list-dot";

                const name = document.createElement("span");
                name.textContent = file.name;

                item.appendChild(dot);
                item.appendChild(name);
                fileList.appendChild(item);
            });
        });
    }

        // Mobile Navbar Toggle
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("open");
        });
    }
