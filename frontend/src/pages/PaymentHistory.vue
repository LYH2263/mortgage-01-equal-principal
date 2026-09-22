<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { methodLabel } from '../methods'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1>
<table>
  <tr><th>编号</th><th>方式</th><th>利息合计</th><th>时间</th></tr>
  <tr v-for="h in items" :key="h.id"><td>#{{ h.id }}</td><td>{{ methodLabel(h.method) }}</td><td>{{ h.total_interest }}</td><td>{{ h.created_at }}</td></tr>
</table>
</div></template>
