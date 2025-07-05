import localFont from 'next/font/local';

export const atkinsonFont = localFont({
  src: [
    {
      path: '../../public/fonts/Atkinson Hyperlegible Next/For Professional Use Only/Web Fonts/WOFF2/AtkinsonHyperlegibleNext-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../../public/fonts/Atkinson Hyperlegible Next/For Professional Use Only/Web Fonts/WOFF2/AtkinsonHyperlegibleNext-Bold.woff2',
      weight: '700',
      style: 'normal',
    },
  ],
  variable: '--font-atkinson',
  display: 'swap',
});