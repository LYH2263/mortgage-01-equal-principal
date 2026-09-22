<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { METHODS, methodLabel } from '../methods'
const method = ref('equal_payment')
const settings = ref({})
onMounted(async () => {
  settings.value = await getJSON('/api/settings')
  if (settings.value.method) method.value = settings.value.method
})
</script>
<template><div class="page"><h1>利率说明</h1>
<p>月利率 = 年利率 / 12 / 100。系统默认还款方式：{{ methodLabel(settings.method) }}。</p>
<label>还款方式
  <select v-model="method"><option v-for="m in METHODS" :key="m.value" :value="m.value">{{ m.label }}</option></select>
</label>
<div v-if="method === 'equal_principal'">
  <h2>等额本金</h2>
  <p>每期本金固定 = 本金 / 期数；当期利息 = 期初余额 × 月利率；月供 = 当期本金 + 当期利息。</p>
  <p>月供逐期递减：首期最高、末期最低，末期把剩余余额一次收干净。利息合计低于等额本息。</p>
</div>
<div v-else>
  <h2>等额本息</h2>
  <p>每月月供固定：月供 = 本金 × 月利率 × (1+月利率)^期数 ÷ ((1+月利率)^期数 − 1)。</p>
  <p>前期利息占比高、本金占比低，末期把余额收干净。</p>
</div>
</div></template>
