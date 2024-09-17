'use client'

import { useState } from 'react'
import DiscoverForm from './discover-form'
import SearchResultsContainer from './search-results-container'
import { fetchServices } from '@/services/api'

type Payload = {
  discoverValue: string
}

export default function DiscoverPage() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [message, setMessage] = useState('')

  const fetchResults = async ({ discoverValue }: Payload) => {
    setLoading(true)
    const fetchedResults = await fetchServices(discoverValue)
    setResults(fetchedResults.services)
    setMessage(fetchedResults.message)
    setLoading(false)
  }

  const handleReset = () => {
    setLoading(false)
    setResults([])
  }

  return (
    <>
      {!results.length ? (
        <DiscoverForm onSubmit={fetchResults} onClear={handleReset} isLoading={loading} />
      ) : (
        <SearchResultsContainer message={message} results={results} />
      )}
    </>
  )
}
