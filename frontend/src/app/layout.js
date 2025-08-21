import "./globals.css";

export const metadata = {
  title: "GPT Clone",
  description: "ChatGPT frontend clone",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="h-screen w-screen flex bg-[#343541] text-white">
        {/* Main chat area (right) */}
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
