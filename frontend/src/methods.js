export const METHODS = [
  { value: 'equal_payment', label: '等额本息' },
  { value: 'equal_principal', label: '等额本金' },
]
export const methodLabel = (v) => (METHODS.find((m) => m.value === v) || {}).label || v || '等额本息'
