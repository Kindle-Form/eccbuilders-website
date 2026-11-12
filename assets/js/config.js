/* Form delivery configuration.
   On a plain static deploy (the current Easypanel/Nixpacks setup), set the
   endpoint URLs here. Leave a string empty until it is configured.
   Do not commit secrets. If a URL contains a token, use the Dockerfile
   path instead and set QUOTE_FORM_ENDPOINT (and the optional overrides)
   as service environment variables. The container entrypoint rewrites
   this file on startup and those variables win.
   See the README. */
window.ECC_CONFIG = {
  quoteEndpoint: "",
  tradeEndpoint: "",
  careersEndpoint: "",
};
