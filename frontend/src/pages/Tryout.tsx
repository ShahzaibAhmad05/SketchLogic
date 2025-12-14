import Container from '../components/layout/Container'
import PageHeader from '../components/layout/PageHeader'
import SketchLogicTryout from '../components/sketchlogic/SketchLogicTryout'

export default function Tryout() {
  return (
    <main>
      <Container>
        <div className="py-10">
          <PageHeader
            title="Try SketchLogic"
            subtitle="Upload a circuit sketch and see detected metadata + labelled image."
          />
          <SketchLogicTryout />
        </div>
      </Container>
    </main>
  )
}
