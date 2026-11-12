(function () {
  const menuBtn = document.getElementById("menu-btn");
  const mobileNav = document.getElementById("mobile-nav");

  function setMenu(open) {
    if (!menuBtn || !mobileNav) return;
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    mobileNav.setAttribute("aria-hidden", open ? "false" : "true");
  }

  if (menuBtn && mobileNav) {
    setMenu(false);
    menuBtn.addEventListener("click", function () {
      const open = menuBtn.getAttribute("aria-expanded") !== "true";
      setMenu(open);
      if (open) {
        const first = mobileNav.querySelector("a");
        if (first) first.focus();
      }
    });
    mobileNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setMenu(false);
      });
    });
  }

  const page = document.body.getAttribute("data-page");
  if (page) {
    document.querySelectorAll("[data-nav]").forEach(function (link) {
      if (link.getAttribute("data-nav") === page) {
        link.setAttribute("aria-current", "page");
      }
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") setMenu(false);
  });

  const slides = document.querySelectorAll("#hero-carousel .hero-slide");
  if (
    slides.length > 1 &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    let index = 0;
    window.setInterval(function () {
      slides[index].classList.remove("is-active");
      index = (index + 1) % slides.length;
      slides[index].classList.add("is-active");
    }, 6500);
  }

  document.querySelectorAll("[data-filter-root]").forEach(function (root) {
    const groups = {};
    root.querySelectorAll("[data-filter-group]").forEach(function (button) {
      const group = button.getAttribute("data-filter-group");
      groups[group] = groups[group] || "all";
      button.addEventListener("click", function () {
        groups[group] = button.getAttribute("data-filter");
        root.querySelectorAll('[data-filter-group="' + group + '"]').forEach(function (peer) {
          peer.setAttribute("aria-pressed", peer === button ? "true" : "false");
        });
        applyFilters(root, groups);
      });
    });
  });

  function applyFilters(root, groups) {
    const cards = root.querySelectorAll("[data-project-card]");
    let shown = 0;
    cards.forEach(function (card) {
      let visible = true;
      Object.keys(groups).forEach(function (group) {
        const wanted = groups[group];
        if (wanted === "all") return;
        const attr = group === "region" ? "data-region" : "data-type";
        if (card.getAttribute(attr) !== wanted) visible = false;
      });
      card.classList.toggle("hidden", !visible);
      if (visible) shown += 1;
    });
    const empty = root.querySelector("[data-filter-empty]");
    if (empty) empty.classList.toggle("hidden", shown !== 0);
    const count = root.querySelector("[data-filter-count]");
    if (count) {
      count.textContent =
        shown === 1 ? "Showing 1 project" : "Showing " + shown + " projects";
    }
  }

  document.querySelectorAll("form[data-form]").forEach(bindForm);

  function endpointFor(kind) {
    const config = window.ECC_CONFIG || {};
    if (kind === "trade" && config.tradeEndpoint) return config.tradeEndpoint;
    if (kind === "careers" && config.careersEndpoint) return config.careersEndpoint;
    return config.quoteEndpoint || "";
  }

  function bindForm(form) {
    const kind = form.getAttribute("data-form");
    const errorBox = form.querySelector("[data-form-error]");
    const successBox = form.querySelector("[data-form-success]");
    const submitBtn = form.querySelector("[type=submit]");
    const defaultLabel = submitBtn ? submitBtn.textContent : "";

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      clearErrors(form, errorBox);

      const honeypot = form.querySelector('input[name="company_website"]');
      if (honeypot && honeypot.value.trim() !== "") {
        showSuccess(form, successBox);
        return;
      }

      const problems = validate(form, kind);
      if (problems.length) {
        showErrors(form, errorBox, problems);
        return;
      }

      const endpoint = endpointFor(kind).trim();
      if (!endpoint) {
        showErrors(form, errorBox, [
          {
            message:
              "This form is not connected to a delivery address yet. Call (561) 245-5044 or email avirzi@eccbuilders.com. The site owner sets QUOTE_FORM_ENDPOINT, or the matching field in assets/js/config.js. See the README.",
          },
        ]);
        return;
      }

      const body = new FormData(form);
      body.set("form_type", kind);
      body.delete("company_website");
      const fileInput = form.querySelector('input[type="file"]');
      if (fileInput && fileInput.files.length === 0) body.delete(fileInput.name);

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      fetch(endpoint, {
        method: "POST",
        body: body,
        headers: { Accept: "application/json, text/plain, */*" },
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Request failed with status " + response.status);
          }
          showSuccess(form, successBox);
        })
        .catch(function () {
          showErrors(form, errorBox, [
            {
              message:
                "The request was not sent. You can call (561) 245-5044 or email avirzi@eccbuilders.com. If this keeps happening, the delivery address may be blocking the browser (it has to allow this site’s origin).",
            },
          ]);
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = defaultLabel;
          }
        });
    });
  }

  function validate(form, kind) {
    const problems = [];
    form.querySelectorAll("input, textarea, select").forEach(function (field) {
      if (field.type === "hidden" || field.name === "company_website") return;
      if (field.type === "file" || field.type === "checkbox") return;
      if (!field.checkValidity()) {
        problems.push({ field: field, message: field.validationMessage });
      }
    });

    if (kind === "quote") {
      const phone = form.querySelector('[name="phone"]');
      if (phone && phone.value.trim()) {
        const digits = phone.value.replace(/\D/g, "");
        if (digits.length < 7) {
          problems.push({
            field: phone,
            message: "Enter a phone number with at least 7 digits.",
          });
        }
      }
      const checked = form.querySelectorAll('input[name="contact_by"]:checked');
      if (!checked.length) {
        const group = form.querySelector('input[name="contact_by"]');
        problems.push({
          field: group,
          message: "Choose how we should contact you — phone, email, or both.",
        });
      }
    }

    const fileInput = form.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length) {
      if (fileInput.files.length > 3) {
        problems.push({
          field: fileInput,
          message: "Attach up to 3 files.",
        });
      }
      const allowed = ["pdf", "jpeg", "jpg", "png"];
      Array.prototype.forEach.call(fileInput.files, function (file) {
        const ext = (file.name.split(".").pop() || "").toLowerCase();
        if (allowed.indexOf(ext) === -1) {
          problems.push({
            field: fileInput,
            message: "Files must be PDF, JPEG, JPG, or PNG.",
          });
        }
        if (file.size > 10 * 1024 * 1024) {
          problems.push({
            field: fileInput,
            message:
              "Each file must be 10 MB or smaller. That limit is only for this form.",
          });
        }
      });
    }
    return problems;
  }

  function clearErrors(form, errorBox) {
    form.querySelectorAll("[aria-invalid]").forEach(function (field) {
      field.removeAttribute("aria-invalid");
    });
    if (errorBox) {
      errorBox.hidden = true;
      errorBox.innerHTML = "";
    }
  }

  function showErrors(form, errorBox, problems) {
    if (!errorBox) return;
    const items = problems
      .map(function (problem) {
        if (problem.field) problem.field.setAttribute("aria-invalid", "true");
        return "<li>" + escapeHtml(problem.message) + "</li>";
      })
      .join("");
    errorBox.innerHTML = "<p>The form was not sent.</p><ul class=\"list-disc pl-5 mt-1\">" + items + "</ul>";
    errorBox.hidden = false;
    errorBox.focus();
  }

  function showSuccess(form, successBox) {
    const fields = form.querySelector("[data-form-fields]");
    const intro = form.querySelector("[data-form-intro]");
    const heading = form.querySelector("[data-form-heading]");
    if (fields) fields.hidden = true;
    if (intro) intro.hidden = true;
    if (heading) heading.hidden = true;
    if (successBox) {
      successBox.hidden = false;
      successBox.focus();
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();
