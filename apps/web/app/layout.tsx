export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{background:'#fafafa', color:'#111', margin:0}}>{children}</body>
    </html>
  );
}