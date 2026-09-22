<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
import { METHODS } from '../methods'
const method = ref('equal_payment')
const out = ref(null)
const load = async () => { out.value = await postJSON('/api/schedule', { principal: 1000000, annual_rate: 3.5, months: 360, method: method.value, persist: false, preview_rows: 12 }) }
load()
</script>
<template><div class="page"><h1>摊还表预览</h1>
<label>还款方式
  <select v-model="method" @change="load"><option v-for="m in METHODS" :key="m.value" :value="m.value">{{ m.label }}</option></select>
</label>
<p v-if="out && out.method === 'equal_principal'">首期月供 {{ out.first_payment }} · 末期月供 {{ out.last_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
<p v-else-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
<table v-if="out">
  <tr><th>期数</th><th>月供</th><th>本金</th><th>利息</th><th>剩余本金</th></tr>
  <tr v-for="r in out.preview" :key="r.period"><td>第{{ r.period }}期</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr>
</table>
</div></template>
