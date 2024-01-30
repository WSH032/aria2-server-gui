<!--
The iframe will automatically set `src` prop to `AriaNg set rpc setting command-api`.
e.g. `${aria_ng_src}/#!/settings/rpc/set?protocol=${protocol}&host=${rpcHost}&port=${rpcPort}&interface=${rpcInterface}&secret=${secret}`
see https://ariang.mayswind.net/command-api.html

`interface` prop: the path of aria2c rpc interface, do not start with `/` and do not end with `/`, e.g: `api/aria2/jsonrpc`
`aria-ng-src` prop: the ariaNg src, do not end with `/`, e.g: `/static/AriaNg`
`secret` prop: the rpc secret which is encoded by url-safe base64, optional
 -->

<template>
  <iframe :src="src">
    <!-- modified from: https://github.com/zauberzeug/nicegui/blob/27d5f217adee5f97e16f4021ca9dbc052beaeae4/nicegui/elements/upload.js -->
    <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">
      <slot :name="slot" v-bind="slotProps || {}"></slot>
    </template>
  </iframe>
</template>

<script>
export default {
  props: {
    interface: {
      type: String,
      required: true,
      validator: (value) => {
        return !value.startsWith("/") && !value.endsWith("/");
      }
    },
    ariaNgSrc: {
      type: String,
      required: true,
      validator: (value) => {
        return !value.endsWith("/");
      }
    },
    secret: {
      type: String,
    },
  },
  computed: {
    src() {
      // see: https://ariang.mayswind.net/command-api.html
      //
      // template: /#!/settings/rpc/set?protocol=${protocol}&host=${rpcHost}&port=${rpcPort}&interface=${rpcInterface}&secret=${secret}
      // e.g: /#!/settings/rpc/set?protocol=http&host=127.0.0.1&port=6800&interface=jsonrpc
      const baseUrl = this.ariaNgSrc + "/#!/settings/rpc/set";

      const isHttps = window.location.protocol === "https:";

      const params = new URLSearchParams({
        protocol: isHttps ? "wss" : "ws",
        host: window.location.hostname,
        port: window.location.port || (isHttps ? "443" : "80"),
        interface: this.interface,
      });

      if (this.secret) {
        params.append("secret", this.secret);
      }

      return baseUrl + "?" + params.toString();
    }
  },
};
</script>
