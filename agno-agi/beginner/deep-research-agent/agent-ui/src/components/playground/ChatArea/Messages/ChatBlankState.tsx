'use client'

const ChatBlankState = () => {
  return (
    <div className="flex h-full flex-col items-center justify-center space-y-6 font-dmmono">
      <div className="flex items-center">
        <h1 className="text-4xl font-semibold tracking-tight text-foreground">🤖 Deep Research Agent</h1>
      </div>
      <p className="text-xl text-muted-foreground max-w-2xl text-center leading-relaxed">
        Your advanced research companion powered by AI. I can perform comprehensive analysis on any topic,
        providing detailed insights backed by reliable web sources.
      </p>
    </div>
  )
}

export default ChatBlankState
