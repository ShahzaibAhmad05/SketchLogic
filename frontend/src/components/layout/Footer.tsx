import Container from './Container'

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <Container>
        <div className="flex flex-col gap-2 py-8 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} IRis</p>
          <p className="text-slate-500">Simulate from Sketches</p>
        </div>
      </Container>
    </footer>
  )
}
