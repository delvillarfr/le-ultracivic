import type { Metadata } from "next";
import { atkinsonFont } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ultra Civic",
  description: "Buy + Retire Polluters' Legal Rights to Emit CO2",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={atkinsonFont.variable}>
        {children}
      </body>
    </html>
  );
}
