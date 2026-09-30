<template>

  <q-page class="flex flex-center" padding>
    <div class="full-width" style="max-width: 400px;">
      <h5 class="q-my-md text-center">
        Login Form
      </h5>

      <q-card class="q-pa-md">

        <q-card-section>

          <q-form @submit="onSubmit" ref="formRef">

            <q-input v-model="email" label="Email" placeholder="email@example.com" filled class="q-mb-md" :rules="[required, isEmailValid]">
              <template v-slot:prepend>
                <q-icon name="mdi-email" />
              </template>
            </q-input>

            <q-input v-model="password" label="Password" placeholder="password" filled class="q-mt-mx" :rules="[required, isPasswordValid]">
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>

            <div class="row q-mb-md">
              <q-checkbox v-model="rememberMeCheckbox" label="Remember Me" class="q-mt-mx col"/>

              <q-btn label="don't have an account?" flat to="/signup" filled class="q-mt-mx col" />
            </div>

            <div class="row q-gutter-sm">
              <q-btn label="login" class="full-width col-3 q-mb-md" color="primary" />

              <q-btn label="forgot password?" class="full-width col-3" color="primary" />
            </div>
          </q-form>

        </q-card-section>
      </q-card>

    </div>
  </q-page>

</template>

<script setup>
import { ref } from 'vue'
import isEmail from 'validator/lib/isEmail'
import isStrongPassword from 'validator/lib/isStrongPassword'

const email = ref('')
const password = ref('')
const rememberMeCheckbox = ref(true)

const required = val => !!val || "This field is required"
const isEmailValid = val => isEmail(val) || "Invalid email format"
const isPasswordValid = val => isStrongPassword(val, { minLowercase: 1, minUppercase: 1, minNumbers: 1, minSymbols: 1}) || "Password must be strong (e.g., 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 symbol)"

</script>
