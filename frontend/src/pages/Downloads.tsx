import Container from '../components/layout/Container'
import PageHeader from '../components/layout/PageHeader'
import Card from '../components/ui/Card'

function DownloadCard({
  title,
  desc,
  items,
}: {
  title: string
  desc: string
  items: { label: string; href: string }[]
}) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-slate-600">{desc}</p>
      <div className="mt-4 space-y-2">
        {items.map((i) => (
          <a
            key={i.label}
            href={i.href}
            className="block rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
          >
            {i.label}
          </a>
        ))}
      </div>
    </Card>
  )
}

export default function Downloads() {
  return (
    <main>
      <Container>
        <div className="py-10">
          <PageHeader
            title="Downloads"
            subtitle="Grab the latest builds for SketchLogic and IRis."
          />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <DownloadCard
              title="SketchLogic"
              desc="Detector backend + any packaged client builds."
              items={[
                // { label: 'GitHub Releases (placeholder)', href: '#' },
                { label: 'View Source Repository', href: 'https://github.com/shahzaibahmad05/SketchLogic' },
              ]}
            />

            <DownloadCard
              title="IRis"
              desc="Circuit simulator compatible with SketchLogic JSON."
              items={[
                // { label: 'GitHub Releases (placeholder)', href: '#' },
                { label: 'View Source Repository', href: 'https://github.com/d-khalid/IRis' },
              ]}
            />
          </div>
        </div>
      </Container>
    </main>
  )
}
