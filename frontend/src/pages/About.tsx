import Container from '../components/layout/Container'
import PageHeader from '../components/layout/PageHeader'
import Card from '../components/ui/Card'

const devs = [
  { name: 'Danyal Khalid', role: 'Developer', github: 'https://github.com/d-khalid' },
  { name: 'Shahzaib Ahmad', role: 'Developer', github: 'https://github.com/shahzaibahmad05' },
]

export default function About() {
  return (
    <main>
      <Container>
        <div className="py-10">
          <PageHeader
            title="About"
            subtitle="Two developers building this sketch-to-simulation tool."
          />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-1">
            {devs.map((d) => (
              <Card key={d.name} className="p-6">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold">{d.name}</h3>
                    <p className="mt-1 text-sm text-slate-600">{d.role}</p>
                  </div>
                  <a
                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium hover:bg-slate-100"
                    href={d.github}
                    target="_blank"
                    rel="noreferrer"
                  >
                    GitHub Profile
                  </a>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </Container>
    </main>
  )
}
