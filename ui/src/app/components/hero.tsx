import Image from 'next/image'
import Link from 'next/link'

export default function Hero() {
  return (
    <div className="relative isolate px-6 pt-14 lg:px-8">
      <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-48">
        <div className="hidden sm:mb-8 sm:flex sm:justify-center">
          <Image
            className="h-14 w-auto mx-12"
            src="/vector-logo.webp"
            alt=""
            width={56}
            height={56}
          />
        </div>
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            Discover your community services!
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            AI-powered community service recommendation tailored for your needs. Developed by the Vector Institute and Ontario 211.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/discover"
              className="rounded-md bg-vectorpurple px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-vectorpurple focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Discover now
            </Link>
            <a href="#" className="text-sm font-semibold leading-6 text-gray-900">
              Learn more <span aria-hidden="true">→</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
