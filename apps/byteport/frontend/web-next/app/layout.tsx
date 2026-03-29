import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/auth-context';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from 'react-hot-toast';
import { AuthKitProvider } from '@workos-inc/authkit-nextjs/components';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono'
});

export const metadata: Metadata = {
  title: {
    default: 'BytePort - Deploy Anywhere',
    template: '%s | BytePort'
  },
  description: 'Deploy anywhere from a single declarative plan. Multi-cloud deployment platform for modern applications.',
  keywords: ['deployment', 'devops', 'cloud', 'infrastructure', 'vercel', 'netlify', 'aws', 'multicloud', 'platform'],
  authors: [{ name: 'BytePort Team' }],
  creator: 'BytePort',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'BytePort - Deploy Anywhere',
    description: 'Deploy anywhere from a single declarative plan.',
    siteName: 'BytePort',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'BytePort - Deploy Anywhere'
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BytePort - Deploy Anywhere',
    description: 'Deploy anywhere from a single declarative plan.',
    images: ['/og-image.png']
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1
    }
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png'
  }
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0F1115' }
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased bg-dark-surface text-dark-onSurface`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <AuthKitProvider>
            <AuthProvider>
              {children}
              <Toaster
                position="top-right"
                toastOptions={{
                  className: '',
                  duration: 4000,
                  style: {
                    background: '#232831',
                    color: '#F5F6F8',
                    border: '1px solid #353C49'
                  },
                  success: {
                    iconTheme: {
                      primary: '#5A8DEE',
                      secondary: '#F5F6F8'
                    }
                  },
                  error: {
                    iconTheme: {
                      primary: '#EF4444',
                      secondary: '#F5F6F8'
                    }
                  }
                }}
              />
            </AuthProvider>
          </AuthKitProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
