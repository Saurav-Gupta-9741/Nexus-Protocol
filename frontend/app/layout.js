import "./globals.css";

export const metadata = {
  title: "Nexus Protocol",
  description: "Agent-to-Agent Communication Engine",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
