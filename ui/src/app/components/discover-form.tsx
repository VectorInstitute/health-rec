'use client'

import { useState } from 'react'

type DiscoverFormProps = {
  onSubmit: (payload: { discoverValue: string }) => void
  onClear: () => void
  isLoading: boolean
}

export default function DiscoverForm({ onSubmit, onClear, isLoading }: DiscoverFormProps) {
  const [discoverValue, setDiscoverValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (discoverValue.trim()) {
      onSubmit({ discoverValue })
    }
  }

  return (
    <div className="relative isolate px-6 pt-14 lg:px-8">
      <div className="mx-auto max-w-2xl py-32 sm:py-32 lg:py-32">
        <div className="col-span-full">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-4xl text-center">
            Discover your community services!
          </h1>
        </div>
        <form onSubmit={handleSubmit} className="mt-8">
          <div className="col-span-full">
            <label htmlFor="discover" className="block text-sm font-medium leading-6 text-gray-900">
              What are you looking for?
            </label>
            <div className="mt-2">
              <textarea
                id="discover"
                name="discover"
                rows={3}
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-vectorpurple sm:text-sm sm:leading-6"
                value={discoverValue}
                onChange={(e) => setDiscoverValue(e.target.value)}
                placeholder="Describe your needs..."
              />
            </div>
            <p className="mt-3 text-sm leading-6 text-gray-600">
              Write a few sentences about yourself and your needs. Any information you provide will help us recommend the best community services tailored for you.
            </p>
          </div>
          <div className="mt-6 flex items-center justify-end gap-x-6">
            <button
              type="button"
              onClick={onClear}
              className="text-sm font-semibold leading-6 text-gray-900"
            >
              Clear
            </button>
            <button
              type="submit"
              disabled={isLoading || !discoverValue.trim()}
              className="rounded-md bg-vectorpurple px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-vectorpurple-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-vectorpurple disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </div>
              ) : (
                'Submit'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
