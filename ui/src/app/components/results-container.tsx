'use client'

import { useState } from 'react'
import ResultCard from './result-card'
import Service, { IService } from './service'

type ResultsProps = {
  results: IService[]
}

export default function Results({ results }: ResultsProps) {
  const [open, setOpen] = useState(false)
  const [selectedService, setSelectedService] = useState<IService | null>(null)

  const handleClick = (service: IService) => {
    setSelectedService(service)
    setOpen(true)
  }

  if (!results || results.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8 sm:text-3xl">
          No relevant services found
        </h1>
      </div>
    )
  }

  return (
    <>
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8 sm:text-3xl">
        Relevant Services
      </h1>
      <hr className="my-2 h-0.5 border-t-0 bg-neutral-100 dark:bg-white/10" />
      <ul role="list" className="divide-y divide-gray-100 overflow-auto max-h-[calc(100vh-200px)]">
        {results.map((result: IService) => (
          <ResultCard key={result.WebsiteAddress} onClick={handleClick} result={result} />
        ))}
      </ul>
      {selectedService && (
        <Service open={open} setOpen={setOpen} service={selectedService} />
      )}
    </>
  )
}
