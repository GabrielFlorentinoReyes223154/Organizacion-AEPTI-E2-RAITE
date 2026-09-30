<template>
  <q-page class="flex flex-center" padding>
    <div class="full-width" style="max-width: 400px;">
      <h5 class="q-my-md text-center">
        Sign Up Form
      </h5>

      <q-card class="q-pa-md">

        <q-card-section>

          <q-form>
            <q-input v-model="name" label="Full Name" placeholder="Full Name" filled class="q-mt-md" :rules="[rules, isEmptyName]">
              <template v-slot:prepend>
                <q-icon name="mdi-account" />
              </template>
            </q-input>

            <q-input v-model="email" label="Email" placeholder="email@example.com" filled class="q-mt-mx" :rules="[rules, isEmailValid]">
              <template v-slot:prepend>
                <q-icon name="mdi-email" />
              </template>
            </q-input>

            <q-input v-model="password" label="Password" type="password" filled class="q-mt-mx" :rules="[required, isPasswordValid]">
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>


            <q-input v-model="confirmPassword" label="Verify Password" type="password" filled class="q-mt-mx" :rules="[required, doPasswordsMatch]">
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
            </q-input>

            <div class="q-mt-sm q-ml-md">
              <q-icon :name="hasMinLength ? 'check' : 'close'" :color="hasMinLength ? 'green' : 'red'" />
              At least 8 characters

              <br />

              <q-icon :name="hasLowercase ? 'check' : 'close'" :color="hasLowercase ? 'green' : 'red'" />
              At least 1 lowercase letter

              <br />

              <q-icon :name="hasUppercase ? 'check' : 'close'" :color="hasUppercase ? 'green' : 'red'" />
              At least 1 uppercase letter

              <br />

              <q-icon :name="hasNumber ? 'check' : 'close'" :color="hasNumber ? 'green' : 'red'" />
              At least 1 number

              <br />

              <q-icon :name="hasSymbol ? 'check' : 'close'" :color="hasSymbol ? 'green' : 'red'" />
              At least 1 symbol (e.g. !@#$)

            </div>

            <q-btn label="already have an account?" flat to="/login" filled class="q-mb-md" />

            <div class="row" filled>

              <q-btn label="signup" class="full-width" color="positive" :disble="!isPasswordValid" />

            </div>

          </q-form>

        </q-card-section>

      </q-card>

    </div>

  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const doPasswordsMatch = val => val === password.value || 'Passwords do not match'

const hasMinLength = computed(() => password.value.length >= 8)
const hasLowercase = computed(() => /[a-z]/.test(password.value))
const hasUppercase = computed(() => /[A-Z]/.test(password.value))
const hasNumber = computed(() => /[0-9]/.test(password.value))
const hasSymbol = computed(() => /[^A-Za-z0-9]/.test(password.value))

const isPasswordValid = computed(() =>
  hasMinLength.value &&
  hasLowercase.value &&
  hasUppercase.value &&
  hasNumber.value &&
  hasSymbol.value
)

</script>
