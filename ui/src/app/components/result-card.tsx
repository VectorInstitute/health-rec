import { IService } from './service'

type ResultCardProps = {
  result: IService
  onClick: (service: IService) => void
}

export default function ResultCard({ result, onClick }: ResultCardProps) {
  if (!result) {
    return null
  }

  const websiteAddress = result.WebsiteAddress || '#'

  return (
    <li
      onClick={() => onClick(result)}
      className="flex justify-between gap-x-6 m-2 py-2 block max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700 cursor-pointer transition duration-300 ease-in-out"
    >
      <div className="flex min-w-0 gap-x-4">
        <div className="min-w-0 flex-auto">
          <p className="text-sm font-semibold leading-6 text-gray-900">{result.PublicName}</p>
          <p className="mt-1 truncate text-xs leading-5 text-gray-500">
            {result.PhysicalAddress1}, {result.PhysicalCity}
          </p>
        </div>
      </div>
      <div className="hidden shrink-0 sm:flex sm:flex-col sm:items-end">
        <a href={websiteAddress} className="text-xs leading-6 text-blue-600 hover:underline" onClick={(e) => e.stopPropagation()}>
          Website
        </a>
        <p className="text-xs leading-5 text-gray-500">{result.Phone1Number}</p>
      </div>
    </li>
  )
}
