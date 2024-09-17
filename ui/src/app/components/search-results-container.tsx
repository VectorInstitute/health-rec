import RecommendationContainer from './recommendation-container'
import ResultsContainer from './results-container'

type SearchResultsContainerProps = {
  message: string
  results: any[]
}

export default function SearchResultsContainer({ message, results }: SearchResultsContainerProps) {
  return (
    <div className="relative isolate px-6 pt-14 lg:px-8">
      <div className="mx-auto w-full max-w-6xl py-32 sm:py-20 lg:py-20">
        <div className="flex flex-col md:flex-row mb-4">
          <div className="w-full md:w-2/3 mx-4 mb-4 md:mb-0">
            <RecommendationContainer message={message} />
          </div>
          <div className="w-full md:w-1/3 mx-4">
            <ResultsContainer results={results} />
          </div>
        </div>
        <hr className="my-2 h-0.5 border-t-0 bg-neutral-100 dark:bg-white/10" />
      </div>
    </div>
  )
}
