const PRODUCT_LABELS: Record<string, string> = {
  coffee: 'Coffee',
  cacao: 'Cacao',
  wine: 'Wine',
}

export function productLabel(product: string): string {
  return PRODUCT_LABELS[product] || product.charAt(0).toUpperCase() + product.slice(1)
}
