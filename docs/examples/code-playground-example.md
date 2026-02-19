# CodePlayground Examples

This page demonstrates the CodePlayground component for interactive code examples.

---

## Python Example

<CodePlayground 
  lang="python" 
  title="Agent Example"
  code="from thegent import Agent

agent = Agent('codex')
result = agent.run('Hello world')
print(result)" 
/>

---

## Bash Example

<CodePlayground 
  lang="bash" 
  title="CLI Example"
  code="thegent run codex 'Fix this bug'
thegent list agents
thegent status" 
/>

---

## JavaScript Example

<CodePlayground 
  lang="javascript" 
  title="API Example"
  code="const agent = new Agent('codex');
const result = await agent.run('Hello world');
console.log(result);" 
/>

---

## Features

- **Copy Code**: Click the 📋 button to copy code
- **Run Code**: Click ▶ Run to execute (ready for API integration)
- **Language Badge**: Shows the programming language
- **Output Display**: Shows execution results or errors
- **Dark Mode**: Automatically adapts to theme

---

**See Also**: [VITEPRESS_USAGE_GUIDE.md](../guides/VITEPRESS_USAGE_GUIDE.md)
