import '../globals.css'

export const metadata = {
  title: 'Aiden.AI',
  description: 'Dein persönlicher KI-Operator',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body className="bg-white text-black min-h-screen">{children}</body>
    </html>
  )
}