// /frontend/app/layout.tsx
export const metadata = {
  title: 'Aiden.AI',
  description: 'Dein persönlicher KI-Operator',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  )
}
