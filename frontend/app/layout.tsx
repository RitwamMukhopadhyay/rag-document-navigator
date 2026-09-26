import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Document Navigator: Agentic and Transparent RAG Assistant',
  description: 'Local PDF question-answering application with explicit retrieval traces, exact [filename:page] citations, and Precision@k evaluation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 antialiased selection:bg-teal-500 selection:text-white min-h-screen">
        {children}
      </body>
    </html>
  );
}
