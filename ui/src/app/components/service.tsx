import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import Markdown from './markdown'

export interface IService {
  PublicName: string
  PhysicalAddress1: string
  PhysicalCity: string
  WebsiteAddress: string
  Phone1Number: string
  Eligibility: string
  ApplicationProcess: string
  DisabilitiesAccess: string
  AgencyDescription: string
  Hours: string
}

type DisplayFieldType = {
  [key: string]: keyof IService
}

const DISPLAY_FIELDS: DisplayFieldType = {
  Name: "PublicName",
  Description: "AgencyDescription",
  Address: "PhysicalAddress1",
  City: "PhysicalCity",
  Website: "WebsiteAddress",
  Hours: "Hours",
  Eligibility: "Eligibility",
  "Application Process": "ApplicationProcess",
  "Disabilities Access": "DisabilitiesAccess"
}

type ServiceProps = {
  open: boolean
  setOpen: (open: boolean) => void
  service: IService
}

export default function Service({ open, setOpen, service }: ServiceProps) {
  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={setOpen}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    onClick={() => setOpen(false)}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900 mb-4">
                      Service Information
                    </Dialog.Title>
                    <div className="mt-2">
                      {Object.entries(DISPLAY_FIELDS).map(([key, value]) => (
                        <div key={key} className="py-4 border-b border-gray-200">
                          <dt className="text-sm font-medium text-gray-500">{key}</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {value === 'WebsiteAddress' ? (
                              <a href={service[value]} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                {service[value] || 'N/A'}
                              </a>
                            ) : (
                              <Markdown markdownText={service[value] || 'N/A'} />
                            )}
                          </dd>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}
