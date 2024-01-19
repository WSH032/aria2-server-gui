<!--
`action` prop: the url that you want to submit to. (this is native html form attribute)
`method` prop: the method that you want to use, default to `post`
`enctype` prop: the enctype that you want to use, default to `application/x-www-form-urlencoded`
`redirect-url` prop: the url that you want to redirect to after succeed submission, default to `""` (current page)
 -->

<template>
  <!-- modified from: https://github.com/zauberzeug/nicegui/blob/27d5f217adee5f97e16f4021ca9dbc052beaeae4/nicegui/elements/upload.js -->
  <q-form @submit.prevent="onSubmit">
    <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">
      <slot :name="slot" v-bind="slotProps || {}"></slot>
    </template>
  </q-form>
</template>

<script>
export default {
  props: {
    redirectUrl: {
      type: String,
      default: ""
    },
    method: {
      type: String,
      validator(value, props) {
        return ['POST', 'PATCH'].includes(value)
      },
      default: "POST",
    },
    enctype: {
      type: String,
      validator(value, props) {
        return ['application/x-www-form-urlencoded', 'application/json'].includes(value)
      },
      default: "application/x-www-form-urlencoded",
    },
  },
  data() {
    return {
      _submitingFlag: false,
    };
  },
  methods: {
    /**
     * @param {SubmitEvent} evt
     * @returns {void}
    */
    async onSubmit(evt) {
      const TIMEOUT = 10000;  // 10s
      const REDIRECT_WAITING = 3000;  // 3s
      const vm = this;
      let submitNotify

      // prevent multiple submission
      if (vm.$data._submitingFlag) {
        Quasar.Notify.create({
          progress: true,
          type: 'info',
          message: "Please wait for previous submission to finish.",
          timeout: TIMEOUT,
        });
        return;
      }

      try {
        vm.$data._submitingFlag = true;

        // create notification for user
        submitNotify = Quasar.Notify.create({
          progress: true,
          type: 'ongoing',
          message: 'Submitting...',
          timeout: 0,  // 0 => forever. will set timeout later in following code
        });

        /** @type {HTMLFormElement} */
        const formElem = evt.target;
        const formData = new FormData(formElem);

        // set fetch init argument
        const method = vm.method;

        const headers = new Headers({
          'Content-Type': vm.enctype,
        });

        let body;
        if (vm.enctype === 'application/json') {
          body = JSON.stringify(Object.fromEntries(formData));
        } else if (vm.enctype === 'application/x-www-form-urlencoded') {
          body = new URLSearchParams(formData);
        } else {
          throw new Error(`Unknown enctype: ${vm.enctype}`);
        }

        // send request
        const response = await fetch(formElem.action, {
          method,
          headers,
          body,
        });
        console.debug(response);

        if (response.ok) {
          const href = vm.redirectUrl;
          const hyperlinks = `<a href="${href}"><strong>HERE</strong></a>`;
          const hrefShowed = href === "" ? "current page" : href;
          submitNotify({
            type: 'positive',
            html: true,
            message: `Success! Redirecting to ${hrefShowed} in ${REDIRECT_WAITING / 1000}s. Click ${hyperlinks} if not redirected.`,
            timeout: REDIRECT_WAITING
          })
          // redirect after a while
          await new Promise(resolve => setTimeout(resolve, REDIRECT_WAITING));
          window.location.assign(href);
          return;
        } else {
          console.log("denial submission", response);
          const data = await response.text()
          submitNotify({
            type: 'negative',
            message: `${response.status} response: ${data}`,
          })
        }
      } catch (error) {
        submitNotify({
          type: 'warning',
          message: "Something went wrong, please see console for details.",
        })
        console.error(error);
      } finally {
        vm._submitingFlag = false;
        // close notification anyway
        submitNotify({
          timeout: TIMEOUT,
        })
      }
    },
  },
};
</script>
