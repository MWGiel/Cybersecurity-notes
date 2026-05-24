# Bun — Overview

## What is Bun?

Bun is a JavaScript runtime, package manager, and test runner designed as a drop-in replacement for Node.js.

## JavaScript Engine

- Bun uses Safari's **JavaScriptCore** as its JavaScript engine
- Unlike Node.js and Deno, which both run on the **V8** engine used by Chromium


# Bun — Capabilities Notes

## Bundling, Minifying & SSR

Bun supports bundling, minifying, and server-side rendering (SSR) for frameworks like Svelte, Nuxt.js, and Vite.

### Bundling
- Combines multiple files and assets (JavaScript, CSS, HTML) into a smaller number of files
- Reduces the number of server requests
- Enhances overall performance

### Minifying
- Compresses files by removing unnecessary characters (whitespace, comments, etc.)
- Does not affect functionality
- Further optimizes website load times
- Bun provides an API to decide whether to preserve some readability (e.g. keeping whitespace)

## Runtime Features

The Bun runtime supports:
- Foreign Function Interface (FFI)
- SQLite3
- TLS 1.3
- DNS resolution

## Built-in Tools

Bun ships bundled with common tools:
- File editing
- HTTP servers
- WebSocket
- Hashing
