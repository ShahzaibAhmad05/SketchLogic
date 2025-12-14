import Card from './Card'

export default function Stat({
  value,
  label,
}: {
  value: string | number
  label: string
}) {
  return (
    <Card className="p-4 text-center">
      <div className="text-xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-slate-600">{label}</div>
    </Card>
  )
}
