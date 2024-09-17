import ReactMarkdown from 'react-markdown'

type MarkdownProps = {
  markdownText: string
}

export default function Markdown({ markdownText }: MarkdownProps) {
  return (
    <ReactMarkdown
      components={{
        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold my-4" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-xl font-semibold my-3" {...props} />,
        h3: ({ node, ...props }) => <h3 className="text-lg font-medium my-2" {...props} />,
        p: ({ node, ...props }) => <p className="my-2" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc list-inside my-2" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal list-inside my-2" {...props} />,
        li: ({ node, ...props }) => <li className="my-1" {...props} />,
        a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
      }}
    >
      {markdownText}
    </ReactMarkdown>
  )
}
