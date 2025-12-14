import Container from '../components/layout/Container'
import PageHeader from '../components/layout/PageHeader'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import { NavLink } from 'react-router-dom'
import banner from '../assets/banner.jpg'

export default function Home() {
  return (
    <main>
      <Container>
        <div className="py-10">
          <img
            src={banner}
            alt="SketchLogic banner"
            className="w-3/7 mx-left max-w-4xl rounded-2xl border border-slate-200 bg-white shadow-sm"
          />

          <div className="mt-8">
            <PageHeader
              title="SketchLogic X IRis"
              subtitle="Detect logic circuit metadata from sketches, then simulate with IRis."
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Card className="p-6">
              <h3 className="text-lg font-semibold">SketchLogic</h3>
              <p className="mt-2 text-slate-600">
                Upload a hand-drawn circuit and get structured JSON metadata (components, wires, connections).
              </p>
              <div className="mt-4 flex gap-2">
                <NavLink to="/sketchlogic"><Button>Learn more</Button></NavLink>
                <NavLink to="/try">
                  <Button className="bg-black text-slate-900 border-slate-300 hover:bg-slate-50">
                    Try it
                  </Button>
                </NavLink>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold">IRis</h3>
              <p className="mt-2 text-slate-600">
                A circuit simulator compatible with SketchLogic JSON: rebuild and simulate your detected circuit.
              </p>
              <div className="mt-4 flex gap-2">
                <NavLink to="/iris"><Button>Learn more</Button></NavLink>
                <NavLink to="/downloads">
                  <Button className="bg-black text-slate-900 border-slate-300 hover:bg-slate-50">
                    Download
                  </Button>
                </NavLink>
              </div>
            </Card>
          </div>
        </div>
      </Container>
    </main>
  )
}
