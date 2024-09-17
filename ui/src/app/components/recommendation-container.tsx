import Markdown from './markdown'

type RecommendationContainerProps = {
  message: string
}

export default function RecommendationContainer({ message }: RecommendationContainerProps) {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8 sm:text-3xl">
        Top Recommendation
      </h1>
      <hr className="my-2 h-0.5 border-t-0 bg-neutral-100 dark:bg-white/10" />
      <Markdown markdownText={message} />
    </div>
  )
}
