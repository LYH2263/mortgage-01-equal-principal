<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
import { METHODS } from '../methods'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const method = ref('equal_payment')
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, method: method.value, persist: true }) }
</script>
<template><div class="page"><h1>月供试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<label>还款方式
  <select v-model="method"><option v-for="m in METHODS" :key="m.value" :value="m.value">{{ m.label }}</option></select>
</label>
<button @click="run">计算</button>
<template v-if="out">
  <p v-if="out.method === 'equal_principal'">首期月供 {{ out.first_payment }} · 末期月供 {{ out.last_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
  <p v-else>月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
  <table>
    <tr><th>期数</th><th>月供</th><th>本金</th><th>利息</th><th>剩余本金</th></tr>
    <tr v-for="r in out.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr>
  </table>
</template>
</div></template>
